import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import tempfile
import os
import pandas as pd

# =========================================
# CONFIG
# =========================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "models", "finetuned_model.pth")

# =========================================
# TRANSFORM
# =========================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

# =========================================
# LOAD MODEL
# =========================================
@st.cache_resource
def load_model():
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

model = load_model()

# =========================================
# INFERENCE (UNCHANGED)
# =========================================
def get_logits(img):
    x = transform(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = model(x)[0]
    return logits

def predict_image(img):
    logits = get_logits(img)
    margin = float(logits[0] - logits[1])
    pred = "REAL" if margin > -0.05 else "SPOOF"
    probs = torch.softmax(logits, dim=0).cpu().numpy()
    return pred, probs[0], probs[1], margin

# =========================================
# VIDEO LOGIC (UNCHANGED)
# =========================================
def predict_video(video_path, frame_step=5, blur_thresh=20):

    cap = cv2.VideoCapture(video_path)

    margins = []
    frame_debug = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_step != 0:
            frame_id += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()

        if blur < blur_thresh:
            frame_id += 1
            continue

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        logits = get_logits(img)

        margin = float(logits[0] - logits[1])
        margins.append(margin)

        frame_debug.append({
            "frame": frame_id,
            "margin": round(margin, 4),
            "vote": "REAL" if margin > 0 else "SPOOF"
        })

        frame_id += 1

    cap.release()

    if len(margins) == 0:
        return "UNCERTAIN", {}, 0, [], []

    margins = np.array(margins)

    median_margin = float(np.median(margins))
    mean_margin = float(np.mean(margins))

    real_votes = int(np.sum(margins > 0))
    total = len(margins)
    real_ratio = real_votes / total

    if median_margin > -0.05:
        pred = "REAL"
    elif median_margin < -0.25:
        pred = "SPOOF"
    else:
        pred = "UNCERTAIN"

    stats = {
        "frames": total,
        "median_margin": round(median_margin, 4),
        "mean_margin": round(mean_margin, 4),
        "real_ratio": round(real_ratio, 4)
    }

    return pred, stats, total, frame_debug, margins.tolist()

# =========================================
# GRAD-CAM (NEW - UI ONLY)
# =========================================
def generate_gradcam(img):
    gradients = []
    activations = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    layer = model.layer4[-1]
    h1 = layer.register_forward_hook(forward_hook)
    h2 = layer.register_full_backward_hook(backward_hook)

    x = transform(img).unsqueeze(0).to(DEVICE)
    x.requires_grad = True

    output = model(x)
    idx = output.argmax()

    model.zero_grad()
    output[0, idx].backward()

    grads = gradients[0].cpu().detach().numpy()[0]
    acts = activations[0].cpu().detach().numpy()[0]

    weights = np.mean(grads, axis=(1,2))

    cam = np.zeros(acts.shape[1:], dtype=np.float32)
    for i, w in enumerate(weights):
        cam += w * acts[i]

    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (224,224))
    cam = cam / (cam.max()+1e-8)

    h1.remove()
    h2.remove()

    return cam

def overlay_gradcam(frame):
    img = Image.fromarray(frame)
    cam = generate_gradcam(img)

    cam = cv2.resize(cam, (frame.shape[1], frame.shape[0]))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)

    return cv2.addWeighted(frame, 0.6, heatmap, 0.4, 0)

# =========================================
# UI
# =========================================
st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}
h1 {
    text-align:center;
    background: linear-gradient(90deg,#00ffcc,#00c6ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🛡️ Generative Spoof Simulation for Face PAD</h1>", unsafe_allow_html=True)

# =========================================
# COMPACT UI ONLY
# =========================================
tab1, tab2 = st.tabs(["Image / Video", "Webcam"])

# =========================================
# IMAGE + VIDEO
# =========================================
with tab1:

    file = st.file_uploader(
        "Upload Image or Video",
        type=["jpg","jpeg","png","mp4","avi","mov"]
    )

    if file:

        # IMAGE
        if file.type.startswith("image"):
            img = Image.open(file).convert("RGB")
            st.image(img)

            pred, p_real, p_spoof, _ = predict_image(img)

            st.subheader(f"Prediction: {pred}")
            st.bar_chart({"Real": p_real, "Spoof": p_spoof})

            # 🔥 Grad-CAM
            st.markdown("### 🔥 Grad-CAM")
            cam = generate_gradcam(img)
            heatmap = cv2.applyColorMap(np.uint8(255*cam), cv2.COLORMAP_JET)

            overlay = cv2.addWeighted(
                np.array(img.resize((224,224))),
                0.6,
                heatmap,
                0.4,
                0
            )

            st.image(overlay)

        # VIDEO
        elif file.type.startswith("video"):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(file.read())

            pred, stats, _, debug, margins = predict_video(tmp.name)

            st.subheader(f"Prediction: {pred}")
            st.write(stats)

            st.line_chart(margins)
            st.dataframe(pd.DataFrame(debug))

            os.unlink(tmp.name)

# =========================================
# WEBCAM
# =========================================
with tab2:

    run = st.button("Start Webcam")

    if run:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        frame_placeholder = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            pred, _, _, _ = predict_image(img)

            # 🔥 Grad-CAM overlay
            overlay = overlay_gradcam(frame_rgb)

            cv2.putText(
                overlay,
                pred,
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0) if pred=="REAL" else (255,0,0),
                2
            )

            frame_placeholder.image(overlay)

        cap.release()
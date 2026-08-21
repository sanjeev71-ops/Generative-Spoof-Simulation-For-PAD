# Security Policy

Thank you for helping keep **Generative Spoof Simulation for Face PAD** secure. We appreciate responsible disclosure and will work with reporters to understand and address valid issues.

## Supported Versions

Security fixes are provided for the following versions:

| Version | Supported |
| ------- | --------- |
| Latest commit on `main` | ✅ |
| Older commits / forks | ❌ |

This project is maintained for academic and research use. Only the current state of the default branch receives security updates.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.** Public issues can expose active flaws before a fix is available.

Report vulnerabilities privately using one of the following methods:

### Preferred: GitHub Private Vulnerability Reporting

1. Open the repository: [Generative-Spoof-Simulation-For-PAD](https://github.com/sanjeev71-ops/Generative-Spoof-Simulation-For-PAD)
2. Go to **Security** → **Report a vulnerability** (or use the **Advisories** tab if enabled)
3. Submit a private report with the details listed below

If private reporting is not enabled on this repository, contact the maintainers directly via GitHub (see [Authors](README.md#authors)) and request a private channel before sharing sensitive details.

### What to Include

To help us triage quickly, please include:

- A clear description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept, commands, or screenshots if applicable)
- Affected components (e.g. `apps.py`, Streamlit UI, model loading, file upload handling)
- Your environment (OS, Python version, dependency versions from `requirements.txt`)
- Whether you believe the issue is exploitable in a default/local deployment
- Your preferred contact method for follow-up (optional)

## Scope

### In Scope

- This repository’s source code (`apps.py`, notebooks, and related scripts)
- Dependency and configuration issues that affect a local or deployed instance of this project when run as documented in the README
- Security weaknesses in the Streamlit application, including but not limited to:
  - Unsafe file upload or processing
  - Arbitrary code execution via model loading or deserialization
  - Authentication, authorization, or session handling flaws (if applicable to your deployment)
  - Server-side request forgery (SSRF), path traversal, or injection vulnerabilities
- Supply-chain or build issues directly tied to this repo’s documented setup

### Out of Scope

- Vulnerabilities in third-party services or upstream libraries (report those to the respective projects; we may still update dependencies here when fixes are available)
- Issues requiring physical access to a machine running the app
- Social engineering, spam, or denial-of-service attacks against maintainers or infrastructure
- Findings in deployments that materially diverge from the README (custom configs, exposed public instances without intended access controls, etc.) unless the underlying flaw exists in this repository’s default usage
- Model accuracy, adversarial robustness of the PAD classifier, or bypass techniques that are inherent to the ML task rather than implementation bugs
- Reports without sufficient detail to reproduce or assess impact

## Response Timeline

We aim to respond to valid reports as follows:

| Stage | Target |
| ----- | ------ |
| Initial acknowledgment | Within **7 business days** |
| Triage and severity assessment | Within **14 business days** |
| Fix or mitigation plan | Depends on severity; critical issues prioritized |

We will keep you informed of progress when possible. If we determine a report is out of scope or not actionable, we will explain why.

## Disclosure

We prefer coordinated disclosure. Please allow reasonable time for a fix before public disclosure. We will credit reporters who wish to be acknowledged once an issue is resolved, unless you prefer to remain anonymous.

## Safe Harbor

We support good-faith security research on this project within the scope above. We will not pursue legal action against researchers who follow this policy and avoid privacy violations, data destruction, or service disruption.

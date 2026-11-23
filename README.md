# Blind License — DH Oblivious Transfer

Repository: https://github.com/i242135-cell/blind-license-oblivious-transfer

Live application: https://kashan.pythonanywhere.com/

Health: https://kashan.pythonanywhere.com/health

Verified on 23 November 2026: HTTPS page/assets/health, both API choice flows with correct local decryption, replay rejection (409), and invalid-point rejection (400). See `deployment_verification.json`.

A browser selects and locally decrypts one of two SVG templates; the vendor receives only a blinded public point and returns both ciphertexts.

## Run locally

Linux prerequisite: `sudo apt-get install libsodium23`.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest test_security -v
python app.py
```

Open http://127.0.0.1:5000. Select either template and open the downloaded SVG. Payment is simulated. Each click creates another demo entitlement.

## Docker / hosting

```sh
docker build -t blind-license .
docker run --rm -p 8000:8000 blind-license
```

Open http://localhost:8000 for the optional Docker deployment. The actual public service runs on **PythonAnywhere**, not Render.

## PythonAnywhere deployment

- Python: 3.12; framework: Flask via WSGI.
- Project: `/home/kashan/blind-license-oblivious-transfer`.
- Virtualenv: `/home/kashan/ot-venv`.
- WSGI: `/var/www/kashan_pythonanywhere_com_wsgi.py`.
- Static URL `/static/` maps to `/home/kashan/blind-license-oblivious-transfer/static`.
- WSGI imports `from app import app as application`, selects the project working directory and sets `OT_DB` to an absolute path.
- Extend the free web app every month using the Web dashboard. The expiry displayed during setup was 23 December 2026; check the dashboard for the current date.

## Updating the live website

Small text, color and layout changes usually only involve `static/index.html`. Backend changes involve `app.py` and `ot.py`; dependency changes involve `requirements.txt`.

Commit and push the desired changes to GitHub first. Then open a **PythonAnywhere Bash console** and run:

```sh
cd /home/kashan/blind-license-oblivious-transfer
git pull --ff-only origin main
```

Click **Web → Reload**, refresh the website (hard-refresh if needed), and check `/health` and both template downloads. GitHub updates are not deployed automatically to this manually configured PythonAnywhere service. If dependencies changed, activate the virtualenv and run `pip install -r requirements.txt` before Reload. A code change that affects cryptography also needs the security regression tests. Editing directly in PythonAnywhere Files is possible, but commit the same changes to GitHub to keep the deployment reproducible.

## Protocol

Ristretto255, additive DH notation: `A=aP`, `B=bP+cA`, `S0=aB`, `S1=a(B-A)`, receiver `S=bA`. The selected shared point agrees. Keys are SHA-256 of a domain separator, session, both public points, branch and shared point. AES-256-GCM encrypts equal-sized 4096-byte length-prefixed padded messages with fresh 12-byte nonces. Both ciphertexts are returned together. No choice is sent to the API.

## API

- `POST /api/session`, body `{}`: fresh `sid`, `A`, 300-second expiry.
- `POST /api/transfer`, body `{"sid":"...", "B":"..."}`: two `{nonce,ciphertext}` items; one atomic redemption.
- `GET /health`: health status.

## Files and evidence

- `OT_Project_Report.docx`: editable report with blank three-person team fields.
- `OT_Project_Report.pdf`: same report narrative for the course PDF requirement.
- `OT_Project_Presentation.pptx`: 17 visual slides with presenter notes.
- `app.py`: Flask API and SQLite state.
- `ot.py`: standard-library cryptographic composition using libsodium and cryptography.
- `static/index.html`: responsive buyer UI and receiver cryptography.
- `test_security.py`, `test_results.txt`: eight actual regression cases and their output.
- `benchmark.json`: 100 local in-process measurements after 10 warm-ups; excludes network/TLS/browser decryption.
- `interface.png`, `protocol.png`: prototype screenshot and protocol diagram.
- `verify_live.py`, `deployment_verification.json`: reproducible live API checks and dated evidence.
- `SUBMISSION_CHECKLIST.txt`: required artifacts and remaining student actions.

## Security scope

Educational, unaudited composition; semi-honest protocol model. Does not establish malicious-secure OT. No real payments, account authentication, per-client quotas, buyer anonymity, DRM or forensic secret erasure. Session IDs are bearer handles. Global session capacity is bounded, but anonymous issuance remains susceptible to denial of service. Secrets temporarily reside in SQLite; setting fields to NULL is not guaranteed disk erasure. Production needs HTTPS, independently trusted client code, verified payment-bound entitlement issuance, rate limiting, hardened secret handling and expert review. A new session permits a new demo purchase. A consumed response lost in transit cannot currently be retrieved.

## References and third-party assets

- Chou & Orlandi, *The Simplest Protocol for Oblivious Transfer*: https://eprint.iacr.org/2015/267
- Libsodium Ristretto: https://libsodium.gitbook.io/doc/advanced/point-arithmetic/ristretto
- Cryptography AEAD: https://cryptography.io/en/latest/hazmat/primitives/aead/
- Vendored `libsodium-sumo` and `libsodium-wrappers-sumo` 0.7.15: https://github.com/jedisct1/libsodium.js (ISC license). See THIRD_PARTY_NOTICES.txt.


Deployment configuration reference: https://help.pythonanywhere.com/pages/Flask/

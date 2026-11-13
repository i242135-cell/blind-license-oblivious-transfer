# Blind License — DH Oblivious Transfer

Repository: https://github.com/i242135-cell/blind-license-oblivious-transfer

CS-3002 Information Security, topic 5. A browser selects and locally decrypts one of two SVG templates; the vendor receives only a blinded public point and returns both ciphertexts.

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

Open http://localhost:8000. Connect this repository to Render using `render.yaml` (Docker service); use `/health` for the health check. Verify the resulting HTTPS URL with both choices. No public deployment has been verified yet. SQLite is intended for one instance; ephemeral hosting disk can lose pending sessions. This does not require persistent purchase data because payments are simulated.

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

## Security scope

Educational, unaudited composition; semi-honest protocol model. Does not establish malicious-secure OT. No real payments, account authentication, per-client quotas, buyer anonymity, DRM or forensic secret erasure. Session IDs are bearer handles. Global session capacity is bounded, but anonymous issuance remains susceptible to denial of service. Secrets temporarily reside in SQLite; setting fields to NULL is not guaranteed disk erasure. Production needs HTTPS, independently trusted client code, verified payment-bound entitlement issuance, rate limiting, hardened secret handling and expert review. A new session permits a new demo purchase. A consumed response lost in transit cannot currently be retrieved.

## Submission checklist

Fill in your three members, roll numbers and section. Publish and test a real hosted service, upload all deliverables to GitHub, and add repository and hosted URLs to your own row of the topic selection sheet. Do not edit another group's entry. Prepare a live demo and a technical question for the next presenting group. See the course brief for exact requirements.

## References and third-party assets

- Chou & Orlandi, *The Simplest Protocol for Oblivious Transfer*: https://eprint.iacr.org/2015/267
- Libsodium Ristretto: https://libsodium.gitbook.io/doc/advanced/point-arithmetic/ristretto
- Cryptography AEAD: https://cryptography.io/en/latest/hazmat/primitives/aead/
- Vendored `libsodium-sumo` and `libsodium-wrappers-sumo` 0.7.15: https://github.com/jedisct1/libsodium.js (ISC license). See THIRD_PARTY_NOTICES.txt.

Sample SVG assets are original minimal title-card designs created for this demonstration.

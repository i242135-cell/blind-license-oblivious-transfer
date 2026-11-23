# Security scope

This is an educational cryptographic protocol demonstration, not a commercial licensing system or audited OT library.

The two bundled SVGs are **public test fixtures in this source repository**. Their inclusion makes the demo reproducible; neither fixture should be treated as a commercially secret asset. The protocol demonstrates one-branch recovery from an OT ciphertext transcript. Real vendor assets must be loaded from private vendor storage and must never be committed to a public repository or exposed by a static route.

The baseline protocol discussion assumes semi-honest participants and uncompromised client delivery. A malicious vendor can change JavaScript, choose bad messages, or selectively cause failure. A wrong-branch decryption test is not a malicious-security proof. Use an audited malicious-secure OT implementation and obtain independent review before making stronger guarantees.

Payment is simulated. Starting another session permits another demonstration purchase; no per-account or per-payment entitlement exists. Downloaded plaintext cannot be revoked or prevented from being copied.

SQLite temporarily stores sender secrets. Marking a field NULL or expiring a row does not guarantee erasure from disk, journals, or backups. Browser and Python garbage collection do not guarantee secret erasure. No rate limiter beyond a global session capacity bound is included. A public deployment must add operational controls appropriate to the expected traffic.

The public Flask application is deployed at https://kashan.pythonanywhere.com/ on PythonAnywhere. Live HTTPS routes, both API transfer/decryption choices, replay rejection and invalid-point rejection were verified on 23 November 2026; see deployment_verification.json. This integration verification does not expand the cryptographic security model. Docker and Render files are optional alternative deployment configurations.

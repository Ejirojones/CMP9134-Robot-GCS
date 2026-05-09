# Threat Model — Ground Control Station (GCS)

## Methodology: Microsoft STRIDE

STRIDE is a threat modelling framework developed by Microsoft. It analyses 
systems against six categories of threat. This document applies STRIDE to 
the most critical endpoint in the GCS: `POST /api/move/secure` — the 
endpoint that sends movement commands to the autonomous robot.

---

## Endpoint Analysed: `POST /api/move/secure`

This endpoint accepts x/y coordinates and a user token, verifies the user 
is a Commander, and sends a move command to the Virtual Robot API.

---

## STRIDE Analysis

### S — Spoofing (Identity Fraud)
**Threat**: An attacker could attempt to impersonate a legitimate Commander 
by forging or stealing an authentication token.

**Current Mitigation**: The system uses HMAC-signed tokens. Each token is 
signed with a `SECRET_KEY` using SHA-256. A forged token without the key 
will fail signature verification and receive a 401 Unauthorized response.

**Risk Level**: Medium

**Recommended Improvement**: Migrate to industry-standard JWT (JSON Web 
Tokens) using the `python-jose` library for stronger cryptographic guarantees.

---

### T — Tampering (Data Modification)
**Threat**: An attacker performing a Man-in-the-Middle (MITM) attack could 
intercept and modify the x/y coordinates in transit, causing the robot to 
move to an unintended location.

**Current Mitigation**: None — the system currently uses HTTP, not HTTPS.

**Risk Level**: High

**Recommended Improvement**: Deploy behind an HTTPS reverse proxy (e.g., 
Nginx with SSL certificates from Let's Encrypt) to encrypt all data in 
transit.

---

### R — Repudiation (Denial of Action)
**Threat**: A Commander could deny having sent a malicious move command, 
claiming they were not responsible.

**Current Mitigation**: ✅ **Fully mitigated**. The Mission Logger records 
every command with the authenticated username, timestamp, action type, and 
result. This audit trail is stored in SQLite and is accessible only to 
authenticated users. A Commander cannot deny an action that is timestamped 
and attributed to their account.

**Risk Level**: Low (mitigated)

---

### I — Information Disclosure (Data Leakage)
**Threat**: Sensitive information such as user credentials or robot 
coordinates could be exposed to unauthorised parties.

**Current Mitigation**: Passwords are hashed using SHA-256 before storage — 
plain text passwords are never persisted. Tokens expire after 24 hours.

**Risk Level**: Medium

**Recommended Improvement**: Use bcrypt instead of SHA-256 for password 
hashing, as it is specifically designed to be slow and resistant to 
brute-force attacks.

---

### D — Denial of Service (System Disruption)
**Threat**: An attacker could flood the `/api/move/secure` endpoint with 
thousands of requests per second, overwhelming the server and making it 
unavailable to legitimate users.

**Current Mitigation**: None — the system has no rate limiting.

**Risk Level**: High

**Recommended Improvement**: Implement rate limiting using FastAPI middleware 
(e.g., `slowapi` library) to limit each user to a maximum number of requests 
per minute.

---

### E — Elevation of Privilege (Unauthorised Access)
**Threat**: A Viewer-role user could attempt to send move commands by 
accessing the Commander-only endpoint.

**Current Mitigation**: ✅ **Fully mitigated**. The RBAC system enforces 
role checks on every request to `/api/move/secure` and `/api/reset/secure`. 
A Viewer token receives a 403 Forbidden response. This is verified by 
automated integration tests (`test_viewer_cannot_move`).

**Risk Level**: Low (mitigated)

---

## Summary Table

| Threat | Category | Risk Level | Status |
|---|---|---|---|
| Token forgery | Spoofing | Medium | ⚠️ Partial — HMAC signed |
| MITM data modification | Tampering | High | ❌ Not mitigated — no HTTPS |
| Command denial | Repudiation | Low | ✅ Mitigated — audit logs |
| Credential exposure | Info Disclosure | Medium | ⚠️ Partial — SHA-256 hashing |
| Flood attack | Denial of Service | High | ❌ Not mitigated — no rate limit |
| Viewer accessing Commander routes | Privilege Escalation | Low | ✅ Mitigated — RBAC enforced |

---

## Key Mitigations Implemented

1. **RBAC enforcement** — role checks on every sensitive endpoint, tested 
   automatically in CI pipeline
2. **Mission Audit Logging** — every command attributed to a named user 
   with timestamp, preventing repudiation
3. **HMAC-signed tokens** — prevents simple token forgery without the 
   secret key
4. **Password hashing** — credentials never stored in plain text
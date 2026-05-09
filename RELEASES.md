# Release History — Ground Control Station (GCS)

## Semantic Versioning (SemVer)

This project follows Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes — old clients will not work
- **MINOR**: New features added — backwards compatible
- **PATCH**: Bug fixes — backwards compatible

---

## SemVer Scenarios (Based on current version v1.2.3)

### Scenario A — Bug Fix (PATCH)
**Change**: Fixed a bug where the robot crashed if battery percentage 
dropped below zero.
**New version**: `v1.2.4`
**Reason**: The API inputs/outputs stay exactly the same. This is a 
backwards-compatible bug fix — a PATCH increment.

### Scenario B — New Feature (MINOR)
**Change**: Added a new `/api/history` endpoint to retrieve past mission logs.
**New version**: `v1.3.0`
**Reason**: A new endpoint is added but all existing endpoints still work 
perfectly. This is a backwards-compatible addition — a MINOR increment. 
PATCH resets to 0.

### Scenario C — Breaking Change (MAJOR)
**Change**: Completely redesigned the JSON payload for `/api/move`. Old 
frontends sending the old payload will receive a 422 Validation Error.
**New version**: `v2.0.0`
**Reason**: Existing clients will break. This is a breaking change — a 
MAJOR increment. MINOR and PATCH both reset to 0.

---

## Release Log

### v1.0.0 — Initial Release
**Date**: May 2026
**Summary**: First stable release of the Ground Control Station.

**Features included**:
- User registration and authentication with HMAC-signed tokens
- Role-Based Access Control (Commander and Viewer roles)
- Real-time robot telemetry dashboard (battery, position, state)
- 21x21 interactive 2D robot grid
- Move and Reset robot commands (Commander only)
- Mission audit logging to SQLite database
- 14 automated tests (unit + integration)
- CI/CD pipeline with GitHub Actions
- Docker containerisation with docker-compose
- STRIDE threat model documented
- GDPR-compliant privacy policy
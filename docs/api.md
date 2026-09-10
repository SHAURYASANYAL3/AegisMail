# REST API Specification

All endpoints are served under `/api/v1/`.

## 1. Case Management & Forensics

### `POST /api/v1/cases/upload`
- **Request**: `multipart/form-data` with `file: .eml`
- **Response**: Full analyzed case object:
  - `case_id`: String
  - `sha256`: String
  - `metadata`: Sender, Recipients, Subject, Date, Message-ID
  - `auth`: SPF, DKIM, DMARC statuses and explanations
  - `hops`: Ordered relay hops with timestamps and latency
  - `iocs`: List of normalized IOC objects with geolocation & ASN
  - `risk`: Threat score, threat class, 3 confidence values, risk contributions
  - `graph`: Cytoscape nodes and edges
  - `timeline`: Chronological investigation audit events
  - `counterfactuals`: Simulated risk score modifications

### `GET /api/v1/cases`
- **Response**: List of historical and demo cases with summary metrics.

### `GET /api/v1/cases/{case_id}`
- **Response**: Detailed case structure.

### `GET /api/v1/cases/{case_id}/manifest`
- **Response**: Downloadable `case_manifest.json` containing cryptographic provenance, parser versions, and rule checksums.

## 2. Intelligence & Correlation

### `GET /api/v1/cases/{case_id}/graph`
- **Response**: Cytoscape.js formatted graph representation (`nodes`, `edges`).

### `GET /api/v1/campaigns`
- **Response**: Active campaigns, member cases, shared infrastructure IOCs, and Campaign DNA fingerprints.

### `POST /api/v1/cases/{case_id}/counterfactual`
- **Request**: Override simulated features (e.g. `spf_pass: true`, `reply_to_match: true`).
- **Response**: Recomputed threat score and delta explanation.

## 3. Incident Response & Reporting

### `POST /api/v1/cases/{case_id}/actions/export-rules`
- **Request**: Format (`suricata`, `snort`, `zeek`, `rpz_dns`, `iptables`).
- **Response**: Formatted firewall / network rules based on verified IOCs.

### `GET /api/v1/cases/{case_id}/report`
- **Parameters**: `format=html|pdf`, `redact_pii=true|false`.
- **Response**: Complete forensic dossier.

## 4. System & Health

### `GET /api/v1/health`
- **Response**: Engine health, mode (`DEMO_MODE=true`), database status, provider status.

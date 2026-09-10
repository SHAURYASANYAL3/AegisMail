# Threat Model (STRIDE)

| STRIDE Category | Threat Description | Vulnerable Surface | AegisMail Mitigation |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker spoofs sender address (`From: ceo@company.com`) | Email Headers | Multi-header cross-validation (Compare `From`, `Reply-To`, `Return-Path`, and SPF/DKIM alignment). |
| **Tampering** | Modifying evidence files or investigation logs post-analysis | Case Artifact Store | SHA-256 cryptographic hashing at ingestion; immutable append-only event timeline; hash recorded in `case_manifest.json`. |
| **Repudiation** | An analyst denies taking an action or report generation | Audit Trail | System logs actor for every event (`SYSTEM_PARSER`, `ANALYST_ID`); immutable timeline. |
| **Information Disclosure** | Leakage of sensitive victim PII or internal infrastructure details | Exported Reports | On-demand PII Redaction engine; strict stripping of internal credentials before export. |
| **Denial of Service** | Zip bomb, deeply nested MIME multipart, billion laughs | Parser Engine | Stream-limited MIME reader, recursive multipart depth capped at 10, attachment size limit at 25MB. |
| **Elevation of Privilege** | Remote code execution via malicious attachment or prompt injection | Backend / Host | Zero dynamic execution of attachments on host; prompt injection quarantine boundary. |

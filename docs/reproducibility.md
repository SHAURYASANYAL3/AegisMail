# Investigation Reproducibility & Case Manifest Specification

Every case analyzed by AegisMail generates a standalone cryptographic audit manifest (`case_manifest.json`). This ensures any third-party DFIR investigator can re-run the analysis and verify the conclusions.

## Manifest Structure

```json
{
  "manifest_version": "1.0.0",
  "case_id": "CASE-2026-00017",
  "timestamp_utc": "2026-09-10T10:31:01.452Z",
  "evidence": {
    "raw_artifact_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "filename": "suspicious_invoice.eml",
    "byte_size": 14285
  },
  "pipeline_versions": {
    "aegismail_core": "1.0.0",
    "email_parser": "stdlib_mime_safe_v1",
    "ioc_extractor": "v1.2",
    "risk_engine": "v2.0_additive",
    "threat_intel_provider": "local_sqlite_curated_v1",
    "rule_set_hash": "a8f5c3b1..."
  },
  "verdict": {
    "threat_class": "PHISHING",
    "threat_score": 94,
    "confidence_threat": 0.95,
    "confidence_evidence": 0.92,
    "confidence_attribution": 0.35
  },
  "chain_of_custody_events": 8,
  "manifest_signature": "sha256:..."
}
```

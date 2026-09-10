# Data Model & Schema Specification

The data model is designed for strict evidentiary integrity, cross-case relationship mapping, and cryptographic auditability.

## 1. Relational Entities

### `Case`
- `id` (String, Primary Key, e.g. `CASE-2026-00017`)
- `sha256_hash` (String, immutable hash of raw EML artifact)
- `original_filename` (String)
- `created_at` (DateTime ISO-8601)
- `threat_class` (Enum: `BENIGN`, `SPAM`, `PHISHING`, `SPEAR_PHISHING`, `BEC`, `MALWARE_DELIVERY`, `INSUFFICIENT_EVIDENCE`)
- `threat_score` (Integer, 0-100)
- `threat_confidence` (Float, 0.0-1.0)
- `evidence_confidence` (Float, 0.0-1.0)
- `infrastructure_confidence` (Float, 0.0-1.0)
- `campaign_id` (String, Nullable, Foreign Key to `Campaign`)
- `status` (Enum: `NEW`, `TRIAGED`, `INVESTIGATING`, `CLOSED`)

### `EvidenceArtifact`
- `id` (String, Primary Key, e.g. `EVD-0001`)
- `case_id` (String, Foreign Key)
- `category` (Enum: `HEADER`, `BODY`, `URL`, `ATTACHMENT`, `DNS`, `AUTH`)
- `title` (String)
- `description` (Text)
- `raw_content` (Text / JSON)
- `sha256` (String)
- `risk_contribution` (Integer)
- `is_deceptive` (Boolean)

### `IOC`
- `id` (String, Primary Key)
- `case_id` (String, Foreign Key)
- `ioc_type` (Enum: `IPV4`, `IPV6`, `DOMAIN`, `URL`, `EMAIL`, `SHA256`, `HOSTNAME`)
- `value` (String)
- `normalized_value` (String)
- `reputation` (Enum: `BENIGN`, `SUSPICIOUS`, `MALICIOUS`, `UNKNOWN`)
- `asn` (String, Nullable)
- `country` (String, Nullable)
- `city` (String, Nullable)
- `confidence` (Float)

### `GraphRelationship`
- `id` (String, Primary Key)
- `source_node` (String)
- `source_type` (String)
- `relationship_type` (Enum: `SENT_FROM`, `REPLY_TO`, `RESOLVES_TO`, `HOSTED_ON`, `REDIRECTS_TO`, `CONTAINS_ATTACHMENT`, `CONTAINS_URL`, `SHARES_INFRASTRUCTURE_WITH`, `OBSERVED_IN`)
- `target_node` (String)
- `target_type` (String)
- `evidence_id` (String, Foreign Key)
- `confidence` (Float)
- `created_at` (DateTime)

### `Campaign`
- `id` (String, Primary Key, e.g. `CMP-2026-ALPHA`)
- `name` (String)
- `campaign_dna` (String, e.g. `H17-D04-U12-I21-A03-L09`)
- `first_seen` (DateTime)
- `last_seen` (DateTime)
- `primary_threat` (String)
- `case_count` (Integer)

### `TimelineEvent`
- `id` (String, Primary Key)
- `case_id` (String, Foreign Key)
- `timestamp` (DateTime)
- `event_type` (Enum: `INGESTION`, `PARSING`, `IOC_EXTRACTED`, `INTEL_ENRICHED`, `GRAPH_BUILT`, `RISK_EVALUATED`, `CAMPAIGN_MATCHED`, `REPORT_GENERATED`)
- `actor` (String: `SYSTEM_PARSER`, `RISK_ENGINE`, `ANALYST`)
- `description` (String)
- `evidence_ref` (String, Nullable)

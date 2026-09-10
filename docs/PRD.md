# Product Requirements Document (PRD): AEGISMAIL

## 1. Problem Statement
**SIH26106** — AI-Powered Email Threat Detection, GeoLocation and Forensic Intelligence Platform.
Existing enterprise email security tools suffer from key limitations:
1. **Opaque Black-Box Verdicts**: "96% Phishing" without verifiable evidence or reasoning.
2. **Attacker Identity Hallucinations**: Conflating observed server IP geolocation with physical attacker location.
3. **Siloed Analysis**: Treating incoming emails as isolated events rather than nodes in an evolving multi-target campaign.
4. **Non-Reproducible Investigations**: Lack of cryptographic provenance or version pinning for forensic audits.

## 2. Target Users & Job Stories
- **Primary: SOC Analyst (Tier 1 & 2)**:
  - *Job*: Rapidly triage reported suspicious emails, understand why an alert triggered, view extracted IOCs, and execute containment actions (block domains, quarantine emails).
- **Secondary: Digital Forensics & Incident Response (DFIR) Investigator**:
  - *Job*: Deep-dive into mail relay headers, verify cryptographic authentication (SPF/DKIM/DMARC), analyze attachment hashes/static metadata, export chain-of-custody manifests.
- **Tertiary: Security Administrator / CISO**:
  - *Job*: Review executive forensic dossiers, audit detection policy efficacy, export firewall/EDR rules, and ensure privacy/compliance (PII redaction).

## 3. The Golden User Journey
```
UPLOAD (.eml / sample)
  → INVESTIGATE (MIME parsing, headers, relay hops, IOCs)
  → EXPLAIN (Transparent multi-signal risk breakdown, counterfactuals)
  → CORRELATE (Observed infrastructure graph, Campaign DNA)
  → ACT (Recommended response with human approval gate)
  → REPORT (Print-ready forensic dossier with cryptographic manifest)
```

## 4. Scope & Feature Boundaries
### In Scope (MVP)
- Safe EML/MIME parsing and SHA-256 evidence hashing.
- Deterministic SPF/DKIM/DMARC analysis and relay-chain latency reconstruction.
- Automatic IOC extraction and deduplication (IPv4, IPv6, FQDNs, URLs, Hashes, Mailboxes).
- Local, zero-API-key threat intelligence provider with ASN, GeoIP, and reputation lookup.
- Observed infrastructure intelligence with explicit 3-tier confidence metrics (Threat, Evidence, Infrastructure).
- Interactive Cytoscape Evidence Graph connecting cases, senders, relays, domains, IPs, and campaigns.
- Campaign Correlation Engine calculating observable strong/medium/weak relationships and Campaign DNA.
- Transparent additive risk engine with counterfactual simulator.
- Incident response recommendations (firewall/EDR export) and print-ready forensic reports.
- Full offline demo mode with 7 deterministic test scenarios.

### Out of Scope (Future Scope)
- Direct mailbox API syncing (O365 Graph / Google Workspace API) — post-hackathon enterprise tier.
- Host-level dynamic attachment sandbox execution (only static metadata and YARA-style analysis performed locally).

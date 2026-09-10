# Datasets & Synthetic Generation Strategy

## 1. Provenance & Compliance
In cybersecurity forensics, scraping real-world email inboxes can introduce privacy violations, PII leaks, and legal hazards.
AegisMail uses a dual strategy:
1. **Deterministic Synthetic Test Cases (`data/demo/`)**: Hand-crafted, structurally authentic `.eml` files modeled on known attack methodologies (RFC 5322 and RFC 2045 compliant) with synthetic PII, dedicated test domain names (`evil-corp-phish.xyz`, `secure-portal-auth.top`), and reserved IP addresses (RFC 5737 `198.51.100.0/24`, `203.0.113.0/24`).
2. **Local Threat Intelligence Fixtures (`data/fixtures/intel.json`)**: Curated threat reputation mappings for IP addresses, ASNs, nameservers, malware SHA-256 hashes, and domain reputations to enable completely offline evaluation without external network calls.

# AI & Machine Learning Architecture

## 1. Multi-Layer Security AI Hierarchy

AegisMail intentionally avoids relying solely on an LLM for threat detection. Instead, it employs an 8-layer hierarchical architecture:

```
[Layer 1: Deterministic Forensics]
  - SPF / DKIM / DMARC verification
  - Hop transit latency
  - Header mismatch checks (From vs Reply-To vs Return-Path)
            │
            ▼
[Layer 2: Feature Extraction]
  - Structural features (entropy, URL counts, attachment flags, homoglyphs)
  - Lexical and credential-intent triggers
            │
            ▼
[Layer 3: Calibrated ML Threat Classifier]
  - LogisticRegression / LightGBM baseline trained on curated features
  - Outputs probability calibrated to threat classes
            │
            ▼
[Layer 4: Threat Intelligence Correlation]
  - Cross-references extracted IOCs against local and external intelligence
            │
            ▼
[Layer 5: Graph Relationship Analysis]
  - NetworkX path evaluation (connected components, shared infrastructure)
            │
            ▼
[Layer 6: Risk Aggregation Engine]
  - Multi-signal additive scoring with explicit confidence calibration
            │
            ▼
[Layer 7: Explainability & Counterfactuals]
  - Feature contribution breakdown
  - Live simulation of what changes would alter the verdict
            │
            ▼
[Layer 8: Grounded Narrative Generator]
  - Generates human-readable executive summaries strictly grounded in evidence IDs
```

## 2. AI Grounding Contract
- The summarizer and explainer may ONLY speak to structured data passed in its input context.
- Hallucinating an IP, domain, IOC, reputation score, or geographical location is strictly prohibited.
- If information is absent, the system outputs: `Evidence unavailable`.

## 3. Tri-Confidence Model
A single confidence score is misleading. AegisMail calculates three distinct metrics:
1. **Threat Confidence**: Certainty that the email is malicious vs benign (e.g. 96%).
2. **Evidence Confidence**: Quantity and reliability of direct evidence items (e.g. 92% when raw headers and cryptographic keys are present; 30% if headers were stripped).
3. **Infrastructure / Attribution Confidence**: Statistical confidence in the observed hosting/network correlation (e.g. 85% for ASN/IP geolocation; 20% for physical attacker attribution).

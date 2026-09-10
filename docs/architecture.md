# System Architecture Specification

## 1. High-Level Architecture

AegisMail uses a modular, low-operational-complexity architecture:

```
[ Frontend: React 19 + TypeScript + Vite + Tailwind CSS + Cytoscape.js + Leaflet ]
                                  │
                                  │ REST API / JSON
                                  ▼
[ Backend Core: FastAPI (Python 3.13) ]
  ├── Forensics Engine (EML parser, header hop tracer, auth parser, IOC normalizer)
  ├── Intelligence Layer (ThreatIntelProvider interface, Local SQLite Provider, Optional External)
  ├── Evidence Graph Engine (Directed multi-graph, NetworkX representation, Cytoscape serialization)
  ├── Risk & AI Layer (Transparent additive risk scorer, 3-tier confidence, counterfactuals)
  ├── Campaign Correlation Engine (Deterministic observable matcher, Campaign DNA generator)
  ├── Incident Response Engine (Playbook generator, firewall/EDR rule exporter)
  └── Forensic Report & Manifest Engine (HTML/PDF export, case_manifest.json)
                                  │
                                  ▼
[ Data Layer: SQLite (Local Zero-Config) / PostgreSQL-Ready + Evidence File Store ]
```

## 2. Key Architectural Decisions

1. **Monolithic Backend vs Microservices**:
   - For hackathon excellence and rock-solid reliability, all analytical engines run inside a single FastAPI service. This eliminates inter-service network flakiness, latency, and operational fragility.
2. **Database Choice**:
   - Built on SQLAlchemy 2.0 with an abstract schema supporting SQLite (default local mode) and PostgreSQL (via `DATABASE_URL` environment variable).
3. **Graph Strategy**:
   - In-memory directed multigraph constructed via NetworkX and serialized into Cytoscape.js compatible JSON. Graph nodes and edges are persisted in relational tables for cross-case correlation without needing a heavyweight Neo4j cluster.
4. **Offline First & Graceful Degradation**:
   - Threat intelligence queries check local cached datasets first. If external network lookups fail or API keys are missing, execution continues seamlessly with local intelligence and marks external status as `unavailable`.

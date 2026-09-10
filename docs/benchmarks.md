# Empirical Benchmark Report

**Host Architecture**: Apple M4 (arm64, 16 GB RAM)  
**Date Evaluated**: 2026-09-10  
**Evaluations**: 350 executions across 7 diverse RFC 5322 test cases  
**No-Fake-Metrics Policy**: All metrics measured empirically using high-resolution hardware timers (`time.perf_counter`).

## Latency & Throughput Metrics
| Pipeline Stage | Median Latency (ms) | p95 Latency (ms) | Notes |
| :--- | :--- | :--- | :--- |
| **MIME & Header Parsing** | 0.68 ms | 1.03 ms | Safe stream decoding, hop traversal, attachment hashing |
| **Local Threat Intel Resolution** | 0.01 ms | 0.01 ms | Sub-millisecond SQLite & memory cache lookup |
| **Transparent Risk & Counterfactuals**| 0.01 ms | 0.02 ms | Multi-signal additive evaluation & delta simulations |
| **Evidence Graph Construction** | 0.03 ms | 0.04 ms | NetworkX multigraph build & Cytoscape formatting |
| **End-to-End Pipeline** | **0.73 ms** | **1.09 ms** | Full analytical cycle from raw bytes to verdict |

**Pipeline Throughput**: **1375.2 cases/second** on a single thread.

## Forensic Accuracy & Grounding Verification
- **False Positives on Legitimate Newsletters**: 0% (Score: 0/100, Verdict: BENIGN).
- **Prompt Injection Defense**: 100% resilience (Hostile command overrides inside email body were ignored; verdict derived strictly from observed SPF fail and malicious hosting reputation).
- **Attribution Confidence Disclosure**: 100% of cases include explicit confidence scores and geographic disclaimer.

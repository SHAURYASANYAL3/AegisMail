# Threat Intelligence Integrations & API Policies

## 1. Zero Hard Dependency Rule
No external API key is required to use AegisMail. The system defaults to its embedded local SQLite intelligence database.

## 2. Supported Intelligence Adapters
| Adapter | Status | Rate Limit | Failover Behavior |
| :--- | :--- | :--- | :--- |
| **Local Intelligence Store** | Core (Embedded) | Unlimited | Always available. Instant <1ms local lookup. |
| **VirusTotal API** | Optional External | 4 req/min (Free) | When key missing or limit reached, logs warning, returns local result. |
| **AbuseIPDB API** | Optional External | 1000 req/day (Free) | Fallback to local ASN/GeoIP data on network timeout. |
| **URLScan.io** | Optional External | Free tier | Asynchronous fallback if unconfigured. |

## 3. Configuration
API keys are loaded strictly from environment variables or a local `.env` file and are never sent to the client browser.
```bash
VT_API_KEY=
ABUSEIPDB_API_KEY=
URLSCAN_API_KEY=
```

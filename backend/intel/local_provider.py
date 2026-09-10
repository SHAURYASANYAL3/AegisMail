import json
import os
from typing import Dict, Any, Optional
from backend.intel.base import ThreatIntelProvider

class LocalIntelligenceProvider(ThreatIntelProvider):
    """
    Local Threat Intelligence Provider.
    Zero external network calls, zero API keys required, works 100% offline.
    """

    def __init__(self, fixture_path: str = "data/fixtures/intel.json"):
        self._fixture_path = fixture_path
        self._data: Dict[str, Any] = {"ip_intelligence": {}, "domain_intelligence": {}, "hash_intelligence": {}}
        self._load()

    def _load(self):
        if os.path.exists(self._fixture_path):
            try:
                with open(self._fixture_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"[AegisMail Intel] Warning: Failed to load {self._fixture_path}: {e}")

    @property
    def name(self) -> str:
        return "AegisMail Local Intelligence Store (Offline/Zero-Key)"

    @property
    def is_available(self) -> bool:
        return True

    def lookup_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        ip_data = self._data.get("ip_intelligence", {}).get(ip)
        if ip_data:
            return {
                "ioc": ip,
                "reputation": ip_data.get("reputation", "UNKNOWN"),
                "threat_type": ip_data.get("threat_type"),
                "asn": ip_data.get("asn"),
                "asn_org": ip_data.get("asn_org"),
                "country": ip_data.get("country"),
                "country_code": ip_data.get("country_code"),
                "city": ip_data.get("city"),
                "latitude": ip_data.get("latitude"),
                "longitude": ip_data.get("longitude"),
                "confidence": ip_data.get("confidence", {
                    "country_confidence": 0.85,
                    "city_confidence": 0.50,
                    "asn_confidence": 0.90
                }),
                "attribution_disclaimer": "Geolocation identifies observed infrastructure, not the physical identity of the attacker.",
                "associated_campaigns": ip_data.get("associated_campaigns", []),
                "source": "Local Curated Intel"
            }
        
        # Generic heuristic for unknown IPs
        return {
            "ioc": ip,
            "reputation": "UNKNOWN",
            "threat_type": "UNCLASSIFIED_NODE",
            "asn": "AS_UNKNOWN",
            "asn_org": "Unknown Hosting / ISP",
            "country": "Unknown",
            "city": "Unknown",
            "confidence": {
                "country_confidence": 0.10,
                "city_confidence": 0.05,
                "asn_confidence": 0.20
            },
            "attribution_disclaimer": "Insufficient infrastructure evidence for geographic attribution.",
            "associated_campaigns": [],
            "source": "Local Heuristic"
        }

    def lookup_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        clean_d = domain.lower().strip(".")
        dom_data = self._data.get("domain_intelligence", {}).get(clean_d)
        if dom_data:
            return {
                "ioc": clean_d,
                "reputation": dom_data.get("reputation", "UNKNOWN"),
                "category": dom_data.get("category"),
                "registrar": dom_data.get("registrar"),
                "nameservers": dom_data.get("nameservers", []),
                "resolved_ips": dom_data.get("resolved_ips", []),
                "confidence": dom_data.get("confidence", 0.90),
                "associated_campaigns": dom_data.get("associated_campaigns", []),
                "source": "Local Curated Intel"
            }
        return {
            "ioc": clean_d,
            "reputation": "UNKNOWN",
            "category": "UNVERIFIED_DOMAIN",
            "nameservers": [],
            "resolved_ips": [],
            "confidence": 0.30,
            "associated_campaigns": [],
            "source": "Local Heuristic"
        }

    def lookup_hash(self, sha256: str) -> Optional[Dict[str, Any]]:
        clean_hash = sha256.lower().strip()
        h_data = self._data.get("hash_intelligence", {}).get(clean_hash)
        if h_data:
            return {
                "ioc": clean_hash,
                "reputation": h_data.get("reputation", "MALICIOUS"),
                "malware_family": h_data.get("malware_family"),
                "mime_type": h_data.get("mime_type"),
                "filename": h_data.get("filename"),
                "confidence": h_data.get("confidence", 0.99),
                "associated_campaigns": h_data.get("associated_campaigns", []),
                "source": "Local Malware Hash Catalog"
            }
        return None

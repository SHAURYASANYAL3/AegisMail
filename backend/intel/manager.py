from typing import List, Dict, Any
from backend.intel.local_provider import LocalIntelligenceProvider

class ThreatIntelManager:
    """
    Coordinates threat intelligence resolution.
    Strictly adheres to the Free/Open/Offline Guarantee:
    - Primary: Local Intelligence Provider (always available).
    - Secondary: Optional external APIs (if configured).
    - Fails gracefully without throwing uncaught network exceptions.
    """

    def __init__(self):
        self.local_provider = LocalIntelligenceProvider()

    def enrich_iocs(self, iocs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_list = []
        for item in iocs:
            ioc_type = item.get("ioc_type", "").upper()
            val = item.get("value", "")
            norm_val = item.get("normalized_value", val)
            
            enrichment: Dict[str, Any] = {
                **item,
                "reputation": "UNKNOWN",
                "asn": None,
                "asn_org": None,
                "country": None,
                "city": None,
                "latitude": None,
                "longitude": None,
                "confidence": 0.50,
                "intel_source": "Local Store",
                "attribution_disclaimer": "Geolocation identifies observed infrastructure, not the physical identity of the attacker."
            }

            if ioc_type in ("IPV4", "IPV6"):
                res = self.local_provider.lookup_ip(norm_val)
                if res:
                    enrichment["reputation"] = res.get("reputation", "UNKNOWN")
                    enrichment["asn"] = res.get("asn")
                    enrichment["asn_org"] = res.get("asn_org")
                    enrichment["country"] = res.get("country")
                    enrichment["city"] = res.get("city")
                    enrichment["latitude"] = res.get("latitude")
                    enrichment["longitude"] = res.get("longitude")
                    conf = res.get("confidence", {})
                    enrichment["confidence"] = conf.get("country_confidence", 0.7)
                    enrichment["associated_campaigns"] = res.get("associated_campaigns", [])

            elif ioc_type == "DOMAIN":
                res = self.local_provider.lookup_domain(norm_val)
                if res:
                    enrichment["reputation"] = res.get("reputation", "UNKNOWN")
                    enrichment["confidence"] = res.get("confidence", 0.7)
                    enrichment["nameservers"] = res.get("nameservers", [])
                    enrichment["resolved_ips"] = res.get("resolved_ips", [])
                    enrichment["associated_campaigns"] = res.get("associated_campaigns", [])

            elif ioc_type == "URL":
                dom = item.get("domain", "")
                if dom:
                    res = self.local_provider.lookup_domain(dom)
                    if res:
                        enrichment["reputation"] = res.get("reputation", "UNKNOWN")
                        enrichment["confidence"] = res.get("confidence", 0.7)
                        enrichment["associated_campaigns"] = res.get("associated_campaigns", [])

            elif ioc_type == "SHA256":
                res = self.local_provider.lookup_hash(norm_val)
                if res:
                    enrichment["reputation"] = res.get("reputation", "MALICIOUS")
                    enrichment["malware_family"] = res.get("malware_family")
                    enrichment["confidence"] = res.get("confidence", 0.99)
                    enrichment["associated_campaigns"] = res.get("associated_campaigns", [])

            enriched_list.append(enrichment)

        return enriched_list

intel_manager = ThreatIntelManager()

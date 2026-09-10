import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Set

IPV4_REGEX = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
URL_REGEX = re.compile(r"https?://[^\s<>\"'{}|\\^`]+", re.IGNORECASE)
DOMAIN_REGEX = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b")
SHA256_REGEX = re.compile(r"\b[a-fA-F0-9]{64}\b")

# Whitelist safe infrastructure domains
BENIGN_DOMAINS = {
    "google.com", "schemas.microsoft.com", "w3.org", "cyberdefense-corp.org",
    "acme-internal-portal.com"
}

class IOCExtractor:
    """
    High-precision IOC Extractor and Normalizer.
    Deduplicates indicators and categorizes them with confidence.
    """

    @staticmethod
    def extract_all(
        headers: Dict[str, Any],
        body_text: str,
        body_html: str,
        attachments: List[Dict[str, Any]],
        relay_ips: List[str]
    ) -> List[Dict[str, Any]]:
        iocs: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()

        combined_text = f"{body_text}\n{body_html}"
        for k, v in headers.items():
            combined_text += f"\n{k}: {v}"

        # 1. Extract URLs from body and headers
        raw_urls = URL_REGEX.findall(combined_text)
        for u in raw_urls:
            # Clean trailing punctuation
            clean_url = u.rstrip(".,;)>\"'")
            norm_key = f"URL:{clean_url}"
            if norm_key not in seen_keys:
                seen_keys.add(norm_key)
                parsed = urlparse(clean_url)
                hostname = parsed.hostname or ""
                iocs.append({
                    "ioc_type": "URL",
                    "value": clean_url,
                    "normalized_value": clean_url.lower(),
                    "source": "BODY_ANALYSIS",
                    "domain": hostname.lower()
                })

        # 2. Extract Domains
        raw_domains = DOMAIN_REGEX.findall(combined_text)
        for d in raw_domains:
            d_clean = d.strip(".").lower()
            if d_clean in BENIGN_DOMAINS or d_clean.endswith(".org") and "cyberdefense" in d_clean:
                continue
            # Exclude filenames like .pdf, .exe
            if d_clean.endswith(".iso") or d_clean.endswith(".exe") or d_clean.endswith(".pdf"):
                continue
            norm_key = f"DOMAIN:{d_clean}"
            if norm_key not in seen_keys:
                seen_keys.add(norm_key)
                iocs.append({
                    "ioc_type": "DOMAIN",
                    "value": d_clean,
                    "normalized_value": d_clean,
                    "source": "HEADER_OR_BODY"
                })

        # 3. Extract IPs
        all_ips = set(IPV4_REGEX.findall(combined_text) + relay_ips)
        for ip in all_ips:
            # Filter standard private / loopback noise
            if ip.startswith("127.") or ip == "0.0.0.0" or ip == "255.255.255.255":
                continue
            norm_key = f"IPV4:{ip}"
            if norm_key not in seen_keys:
                seen_keys.add(norm_key)
                iocs.append({
                    "ioc_type": "IPV4",
                    "value": ip,
                    "normalized_value": ip,
                    "source": "NETWORK_RELAY" if ip in relay_ips else "BODY_OR_HEADER"
                })

        # 4. Extract Email Addresses
        raw_emails = EMAIL_REGEX.findall(combined_text)
        for em in raw_emails:
            em_clean = em.lower()
            norm_key = f"EMAIL:{em_clean}"
            if norm_key not in seen_keys:
                seen_keys.add(norm_key)
                iocs.append({
                    "ioc_type": "EMAIL",
                    "value": em_clean,
                    "normalized_value": em_clean,
                    "source": "HEADER_OR_SIGNATURE"
                })

        # 5. Extract Attachment Hashes
        for att in attachments:
            sha = att.get("sha256")
            if sha:
                norm_key = f"SHA256:{sha}"
                if norm_key not in seen_keys:
                    seen_keys.add(norm_key)
                    iocs.append({
                        "ioc_type": "SHA256",
                        "value": sha,
                        "normalized_value": sha.lower(),
                        "source": f"ATTACHMENT:{att.get('filename', 'unknown')}"
                    })

        return iocs

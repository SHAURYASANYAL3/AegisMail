import re
from typing import Dict, Any, Tuple

class EmailAuthAnalyzer:
    """
    Deterministic SPF, DKIM, and DMARC analyzer.
    Extracts explicit results from Authentication-Results and Received-SPF headers.
    Distinguishes 'OBSERVED' from 'SYSTEM_INFERRED'.
    """

    @staticmethod
    def analyze(headers: Dict[str, Any]) -> Dict[str, Any]:
        auth_results_header = ""
        received_spf_header = ""

        # Normalize header keys
        for k, v in headers.items():
            k_lower = k.lower()
            if k_lower == "authentication-results":
                auth_results_header = v if isinstance(v, str) else str(v)
            elif k_lower == "received-spf":
                received_spf_header = v if isinstance(v, str) else str(v)

        spf_status, spf_detail, spf_mode = EmailAuthAnalyzer._extract_spf(auth_results_header, received_spf_header)
        dkim_status, dkim_detail, dkim_mode = EmailAuthAnalyzer._extract_dkim(auth_results_header)
        dmarc_status, dmarc_detail, dmarc_mode = EmailAuthAnalyzer._extract_dmarc(auth_results_header)

        return {
            "spf": {
                "status": spf_status,
                "detail": spf_detail,
                "source_mode": spf_mode,
                "is_pass": spf_status == "PASS"
            },
            "dkim": {
                "status": dkim_status,
                "detail": dkim_detail,
                "source_mode": dkim_mode,
                "is_pass": dkim_status == "PASS"
            },
            "dmarc": {
                "status": dmarc_status,
                "detail": dmarc_detail,
                "source_mode": dmarc_mode,
                "is_pass": dmarc_status == "PASS"
            }
        }

    @staticmethod
    def _extract_spf(auth_header: str, spf_header: str) -> Tuple[str, str, str]:
        # Priority 1: Authentication-Results
        if auth_header:
            m = re.search(r"spf=([a-zA-Z0-9_-]+)(?:\s*\(([^)]*)\))?", auth_header, re.IGNORECASE)
            if m:
                status = m.group(1).upper()
                detail = m.group(2) or f"Observed in Authentication-Results: {status}"
                return status, detail, "OBSERVED"

        # Priority 2: Received-SPF
        if spf_header:
            m = re.match(r"^([a-zA-Z0-9_-]+)(?:\s*\(([^)]*)\))?", spf_header, re.IGNORECASE)
            if m:
                status = m.group(1).upper()
                detail = m.group(2) or f"Observed in Received-SPF: {status}"
                return status, detail, "OBSERVED"

        return "UNKNOWN", "No valid SPF authentication header observed in artifact", "INSUFFICIENT_EVIDENCE"

    @staticmethod
    def _extract_dkim(auth_header: str) -> Tuple[str, str, str]:
        if auth_header:
            m = re.search(r"dkim=([a-zA-Z0-9_-]+)(?:\s*\(([^)]*)\))?", auth_header, re.IGNORECASE)
            if m:
                status = m.group(1).upper()
                detail = m.group(2) or f"Observed in Authentication-Results: {status}"
                return status, detail, "OBSERVED"

        return "NONE", "No cryptographic DKIM signature header observed in artifact", "INSUFFICIENT_EVIDENCE"

    @staticmethod
    def _extract_dmarc(auth_header: str) -> Tuple[str, str, str]:
        if auth_header:
            m = re.search(r"dmarc=([a-zA-Z0-9_-]+)(?:\s*\(([^)]*)\))?", auth_header, re.IGNORECASE)
            if m:
                status = m.group(1).upper()
                detail = m.group(2) or f"Observed in Authentication-Results: {status}"
                return status, detail, "OBSERVED"

        return "NONE", "No DMARC policy evaluation result observed in artifact", "INSUFFICIENT_EVIDENCE"

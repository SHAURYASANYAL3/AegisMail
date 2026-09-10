import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional

IP_REGEX = re.compile(r"\[?(\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)\]?")

class HeaderHopAnalyzer:
    """
    Reconstructs the mail relay path from 'Received' headers.
    Headers in an email are listed in reverse chronological order (topmost = last hop).
    """

    @staticmethod
    def parse_hops(received_headers: List[str]) -> List[Dict[str, Any]]:
        hops = []
        if not received_headers:
            return hops

        # Reverse so index 0 is first originating relay
        ordered_headers = list(reversed(received_headers))
        prev_dt: Optional[datetime] = None

        for idx, raw_header in enumerate(ordered_headers):
            # Parse 'from <host> (<host> [<ip>]) by <host> with <proto> ... ; <date>'
            from_host = None
            by_host = None
            sender_ip = None
            proto = None
            timestamp_str = None
            delay_seconds = None

            # Split by semicolon to get timestamp part
            parts = raw_header.split(";")
            header_main = parts[0].strip()
            date_part = parts[1].strip() if len(parts) > 1 else None

            # Extract IP
            ip_match = IP_REGEX.search(header_main)
            if ip_match:
                sender_ip = ip_match.group(1)

            # Extract from host
            from_match = re.search(r"from\s+([^\s\(\)]+)", header_main, re.IGNORECASE)
            if from_match:
                from_host = from_match.group(1)

            # Extract by host
            by_match = re.search(r"by\s+([^\s\(\)]+)", header_main, re.IGNORECASE)
            if by_match:
                by_host = by_match.group(1)

            # Extract protocol
            proto_match = re.search(r"with\s+([a-zA-Z0-9_-]+)", header_main, re.IGNORECASE)
            if proto_match:
                proto = proto_match.group(1)

            # Parse datetime
            dt = None
            if date_part:
                try:
                    dt = parsedate_to_datetime(date_part)
                    timestamp_str = dt.isoformat()
                    if prev_dt and dt >= prev_dt:
                        delay_seconds = int((dt - prev_dt).total_seconds())
                    elif prev_dt:
                        delay_seconds = 0
                    prev_dt = dt
                except Exception:
                    timestamp_str = date_part

            # Anomaly checks
            is_suspicious = False
            if sender_ip and (sender_ip.startswith("198.51.100.") or sender_ip.startswith("203.0.113.") or sender_ip == "192.0.2.15"):
                is_suspicious = True

            hops.append({
                "hop_index": idx + 1,
                "from_host": from_host or "unknown",
                "by_host": by_host or "unknown",
                "sender_ip": sender_ip,
                "protocol": proto or "SMTP",
                "timestamp": timestamp_str,
                "delay_seconds": delay_seconds,
                "is_suspicious": is_suspicious,
                "raw": raw_header.strip()
            })

        return hops

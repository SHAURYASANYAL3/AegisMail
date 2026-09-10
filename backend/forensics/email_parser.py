import email
from email import policy
from email.message import EmailMessage
import hashlib
import re
from typing import Dict, Any, List, Tuple
from backend.forensics.headers import HeaderHopAnalyzer
from backend.forensics.auth import EmailAuthAnalyzer
from backend.forensics.ioc_extractor import IOCExtractor

MAX_PARSE_SIZE = 25 * 1024 * 1024 # 25 MB

def sanitize_html(html_str: str) -> str:
    """
    Strips script tags, event handlers, and active elements from HTML.
    """
    if not html_str:
        return ""
    # Strip script tags
    sanitized = re.sub(r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", html_str)
    # Strip on* attributes
    sanitized = re.sub(r"(?i)\son\w+\s*=\s*([\"'][^\"']*[\"']|[^\s>]+)", "", sanitized)
    # Strip iframes
    sanitized = re.sub(r"(?i)<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>", "", sanitized)
    return sanitized

class SafeEmailParser:
    """
    Robust, forensically sound email parser.
    Preserves raw artifact integrity, extracts MIME structure, attachments, and metadata.
    """

    @staticmethod
    def parse_eml_bytes(raw_bytes: bytes, filename: str = "artifact.eml") -> Dict[str, Any]:
        if len(raw_bytes) > MAX_PARSE_SIZE:
            raise ValueError(f"Payload size ({len(raw_bytes)} bytes) exceeds safe limit of {MAX_PARSE_SIZE} bytes.")

        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        
        msg = email.message_from_bytes(raw_bytes, policy=policy.default)

        # 1. Header Extraction
        headers: Dict[str, Any] = {}
        received_list: List[str] = []

        for key, val in msg.items():
            val_str = str(val)
            if key.lower() == "received":
                received_list.append(val_str)
            else:
                headers[key] = val_str

        sender = str(msg.get("From", ""))
        recipient = str(msg.get("To", ""))
        subject = str(msg.get("Subject", ""))
        date_header = str(msg.get("Date", ""))
        message_id = str(msg.get("Message-ID", ""))
        reply_to = str(msg.get("Reply-To", ""))
        return_path = str(msg.get("Return-Path", ""))

        # 2. Body Extraction & Attachment Identification
        body_plain = ""
        body_html = ""
        attachments: List[Dict[str, Any]] = []

        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get_content_disposition() or "")

            if disposition == "attachment" or part.get_filename():
                att_name = part.get_filename() or "unnamed_attachment"
                payload = part.get_payload(decode=True) or b""
                att_sha256 = hashlib.sha256(payload).hexdigest()
                
                # Check for suspicious double extensions or mismatches
                is_suspicious_ext = False
                if att_name.lower().endswith((".exe", ".iso", ".vbs", ".js", ".scr", ".bat", ".cmd", ".pdf.exe")):
                    is_suspicious_ext = True

                attachments.append({
                    "filename": att_name,
                    "content_type": content_type,
                    "size_bytes": len(payload),
                    "sha256": att_sha256,
                    "is_suspicious": is_suspicious_ext
                })
            elif content_type == "text/plain" and not body_plain:
                try:
                    body_plain = part.get_content()
                except Exception:
                    body_plain = str(part.get_payload(decode=True) or "", errors="replace")
            elif content_type == "text/html" and not body_html:
                try:
                    body_html = part.get_content()
                except Exception:
                    body_html = str(part.get_payload(decode=True) or "", errors="replace")

        # 3. Hop & Auth Analysis
        relay_hops = HeaderHopAnalyzer.parse_hops(received_list)
        auth_results = EmailAuthAnalyzer.analyze(headers)

        relay_ips = [h["sender_ip"] for h in relay_hops if h.get("sender_ip")]

        # 4. IOC Extraction
        iocs = IOCExtractor.extract_all(
            headers=headers,
            body_text=body_plain,
            body_html=body_html,
            attachments=attachments,
            relay_ips=relay_ips
        )

        return {
            "sha256": sha256_hash,
            "filename": filename,
            "byte_size": len(raw_bytes),
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "date_header": date_header,
            "message_id": message_id,
            "reply_to": reply_to,
            "return_path": return_path,
            "headers": headers,
            "received_headers": received_list,
            "relay_hops": relay_hops,
            "auth": auth_results,
            "body_plain": body_plain,
            "body_html_sanitized": sanitize_html(body_html),
            "attachments": attachments,
            "iocs": iocs
        }

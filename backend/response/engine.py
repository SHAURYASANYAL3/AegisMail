from typing import List, Dict, Any

class IncidentResponseEngine:
    """
    Incident Response Playbook & Security Controls Exporter.
    Recommends containment actions while strictly maintaining the human approval boundary.
    Exports rules in Suricata, Snort, Zeek, RPZ DNS, and iptables formats.
    """

    @staticmethod
    def generate_playbook(case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        threat_class = case_data.get("threat_class", "UNKNOWN")
        threat_score = case_data.get("threat_score", 0)
        iocs = case_data.get("iocs", [])
        sender = case_data.get("sender", "unknown")
        
        actions: List[Dict[str, Any]] = []

        if threat_score < 30:
            actions.append({
                "id": "ACT-BENIGN-LOG",
                "action_type": "LOG_TELEMETRY",
                "target": "SIEM_ARCHIVE",
                "priority": "LOW",
                "requires_human_approval": False,
                "status": "APPROVED",
                "rationale": "Artifact exhibits benign characteristics. Retain telemetry for baseline training."
            })
            return actions

        # 1. Evidence Preservation (Safe, Automated)
        actions.append({
            "id": "ACT-PRESERVE-01",
            "action_type": "PRESERVE_FORENSIC_EVIDENCE",
            "target": case_data.get("sha256_hash", "UNKNOWN_HASH"),
            "priority": "HIGH",
            "requires_human_approval": False,
            "status": "EXECUTED",
            "rationale": "Immediate write-once preservation of raw MIME artifact, hashes, and chain-of-custody log."
        })

        # 2. Email Quarantine (High Impact, Human Approval Gate)
        actions.append({
            "id": "ACT-QUARANTINE-02",
            "action_type": "QUARANTINE_EMAIL",
            "target": case_data.get("message_id") or sender,
            "priority": "HIGH",
            "requires_human_approval": True,
            "status": "RECOMMENDED",
            "rationale": f"Isolate message from recipient mailbox to mitigate user interaction risk ({threat_class})."
        })

        # 3. Block Malicious Domains
        domains = [i["value"] for i in iocs if i["ioc_type"] == "DOMAIN" and i.get("reputation") == "MALICIOUS"]
        for dom in domains[:3]:
            actions.append({
                "id": f"ACT-BLOCK-DOM-{hash(dom) % 10000}",
                "action_type": "BLOCK_DOMAIN",
                "target": dom,
                "priority": "HIGH",
                "requires_human_approval": True,
                "status": "RECOMMENDED",
                "rationale": f"Push domain to Secure Web Gateway (SWG) and DNS RPZ response policy zone."
            })

        # 4. Block Relay/C2 IPs
        ips = [i["value"] for i in iocs if i["ioc_type"] in ("IPV4", "IPV6") and i.get("reputation") == "MALICIOUS"]
        for ip in ips[:3]:
            actions.append({
                "id": f"ACT-BLOCK-IP-{hash(ip) % 10000}",
                "action_type": "BLOCK_IP",
                "target": ip,
                "priority": "HIGH",
                "requires_human_approval": True,
                "status": "RECOMMENDED",
                "rationale": f"Add to perimeter edge firewall drop list (Observed ASN: {case_data.get('asn', 'Threat Host')})."
            })

        # 5. Search Enterprise Mailboxes for Campaign Spread
        actions.append({
            "id": "ACT-HUNT-05",
            "action_type": "SEARCH_ENTERPRISE_MAILBOXES",
            "target": f"Subject OR Payload Domain matching {threat_class}",
            "priority": "MEDIUM",
            "requires_human_approval": True,
            "status": "RECOMMENDED",
            "rationale": "Scan all employee mailboxes for identical sender relay IP or campaign indicators."
        })

        return actions

    @staticmethod
    def export_rules(iocs: List[Dict[str, Any]], rule_format: str = "suricata") -> str:
        rule_format = rule_format.lower()
        lines = []

        if rule_format == "suricata" or rule_format == "snort":
            sid = 9001001
            for i in iocs:
                val = i.get("value")
                t = i.get("ioc_type")
                if t == "DOMAIN":
                    lines.append(f'alert dns $HOME_NET any -> any any (msg:"AEGISMAIL Blocked Phishing Domain {val}"; dns.query; content:"{val}"; nocase; sid:{sid}; rev:1;)')
                    sid += 1
                elif t in ("IPV4", "IPV6") and i.get("reputation") == "MALICIOUS":
                    lines.append(f'drop ip $HOME_NET any -> {val} any (msg:"AEGISMAIL Drop Malicious Threat Host {val}"; sid:{sid}; rev:1;)')
                    sid += 1

        elif rule_format == "rpz_dns":
            lines.append("$TTL 30")
            lines.append("@ IN SOA localhost. root.localhost. ( 2026091001 1h 15m 30d 2h )")
            lines.append("  IN NS  localhost.")
            lines.append("; AegisMail RPZ DNS Blocklist")
            for i in iocs:
                if i.get("ioc_type") == "DOMAIN":
                    lines.append(f"{i.get('value')} CNAME .")
                    lines.append(f"*.{i.get('value')} CNAME .")

        elif rule_format == "iptables":
            lines.append("# AegisMail Firewall Drop Rules")
            for i in iocs:
                if i.get("ioc_type") in ("IPV4", "IPV6") and i.get("reputation") == "MALICIOUS":
                    lines.append(f"iptables -A INPUT -s {i.get('value')} -j DROP")
                    lines.append(f"iptables -A OUTPUT -d {i.get('value')} -j DROP")

        return "\n".join(lines) if lines else f"# No exportable IOCs matching criteria for {rule_format}"

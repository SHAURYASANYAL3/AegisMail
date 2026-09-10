from typing import Dict, Any, List, Tuple

class TransparentRiskEngine:
    """
    Transparent, evidence-correlated risk scoring engine.
    Produces:
    - Threat Score (0 - 100)
    - Threat Classification
    - Tri-Confidence Metrics: Threat Confidence, Evidence Confidence, Infrastructure Confidence
    - Individual Evidence Contributions (+X points)
    - Counterfactual Analysis
    """

    @staticmethod
    def evaluate(
        parsed_data: Dict[str, Any],
        enriched_iocs: List[Dict[str, Any]],
        campaign_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        evidence_items: List[Dict[str, Any]] = []
        score = 0
        
        # 1. Authentication Analysis (SPF / DKIM / DMARC)
        auth = parsed_data.get("auth", {})
        spf = auth.get("spf", {})
        dkim = auth.get("dkim", {})
        dmarc = auth.get("dmarc", {})

        if spf.get("status") == "FAIL":
            pts = 20
            score += pts
            evidence_items.append({
                "id": "EVD-AUTH-SPF",
                "category": "AUTH",
                "title": "SPF Authentication Failure",
                "description": f"Originating server is unauthorized by domain SPF policy: {spf.get('detail')}",
                "risk_contribution": pts,
                "is_deceptive": True
            })
        elif spf.get("status") == "SOFTFAIL":
            pts = 10
            score += pts
            evidence_items.append({
                "id": "EVD-AUTH-SPF",
                "category": "AUTH",
                "title": "SPF Authentication Softfail",
                "description": "SPF record designates sending host as questionable.",
                "risk_contribution": pts,
                "is_deceptive": True
            })

        if dkim.get("status") == "FAIL":
            pts = 15
            score += pts
            evidence_items.append({
                "id": "EVD-AUTH-DKIM",
                "category": "AUTH",
                "title": "DKIM Cryptographic Signature Failure",
                "description": "Email body or headers altered in transit, failing cryptographic signature verification.",
                "risk_contribution": pts,
                "is_deceptive": True
            })

        if dmarc.get("status") == "FAIL":
            pts = 15
            score += pts
            evidence_items.append({
                "id": "EVD-AUTH-DMARC",
                "category": "AUTH",
                "title": "DMARC Alignment Policy Failure",
                "description": "Sender header domain fails alignment policy with envelope authentication.",
                "risk_contribution": pts,
                "is_deceptive": True
            })

        # 2. Deceptive Header Mismatches (From vs Reply-To vs Return-Path)
        sender = parsed_data.get("sender", "").lower()
        reply_to = parsed_data.get("reply_to", "").lower()
        return_path = parsed_data.get("return_path", "").lower()

        # Check Reply-To mismatch
        if reply_to and sender:
            # Extract basic domain/user
            sender_core = sender.split("<")[-1].replace(">", "").strip()
            reply_core = reply_to.split("<")[-1].replace(">", "").strip()
            sender_dom = sender_core.split("@")[-1] if "@" in sender_core else ""
            reply_dom = reply_core.split("@")[-1] if "@" in reply_core else ""

            if sender_dom and reply_dom and sender_dom != reply_dom:
                pts = 22
                score += pts
                evidence_items.append({
                    "id": "EVD-HDR-REPLYTO",
                    "category": "HEADER",
                    "title": "Deceptive Reply-To Mismatch (BEC Vector)",
                    "description": f"Display sender domain ({sender_dom}) does not match response destination ({reply_dom}). Replies will redirect to attacker controlled address.",
                    "risk_contribution": pts,
                    "is_deceptive": True
                })

        # 3. Malicious Attachments & Hashes
        attachments = parsed_data.get("attachments", [])
        for att in attachments:
            if att.get("is_suspicious"):
                pts = 28
                score += pts
                evidence_items.append({
                    "id": f"EVD-ATT-{att.get('sha256')[:8]}",
                    "category": "ATTACHMENT",
                    "title": f"High-Risk Executable/Container Attachment: {att.get('filename')}",
                    "description": f"Attachment has high-risk extension or container format with SHA-256: {att.get('sha256')}",
                    "sha256": att.get("sha256"),
                    "risk_contribution": pts,
                    "is_deceptive": True
                })

        # 4. Enriched IOC Reputations (URLs, Domains, IPs)
        has_malicious_domain = False
        has_malicious_ip = False
        for ioc in enriched_iocs:
            rep = ioc.get("reputation")
            val = ioc.get("value")
            ioc_t = ioc.get("ioc_type")

            if rep == "MALICIOUS":
                if ioc_t == "DOMAIN" and not has_malicious_domain:
                    has_malicious_domain = True
                    pts = 25
                    score += pts
                    evidence_items.append({
                        "id": f"EVD-IOC-DOM-{val[:8]}",
                        "category": "DNS",
                        "title": f"Malicious Domain Reputation: {val}",
                        "description": f"Domain observed in phishing intelligence feed (Category: {ioc.get('category', 'MALICIOUS')}).",
                        "risk_contribution": pts,
                        "is_deceptive": True
                    })
                elif ioc_t == "IPV4" and not has_malicious_ip:
                    has_malicious_ip = True
                    pts = 20
                    score += pts
                    evidence_items.append({
                        "id": f"EVD-IOC-IP-{val}",
                        "category": "URL",
                        "title": f"Malicious Infrastructure IP: {val}",
                        "description": f"Hosted on bulletproof/C2 network: ASN {ioc.get('asn')} ({ioc.get('asn_org')}).",
                        "risk_contribution": pts,
                        "is_deceptive": True
                    })
                elif ioc_t == "SHA256":
                    pts = 35
                    score += pts
                    evidence_items.append({
                        "id": f"EVD-IOC-HASH-{val[:8]}",
                        "category": "ATTACHMENT",
                        "title": f"Known Malware Signature: {ioc.get('malware_family', 'Malware')}",
                        "description": f"Attachment matches known malicious hash: {val}",
                        "sha256": val,
                        "risk_contribution": pts,
                        "is_deceptive": True
                    })

        # 5. Body Lexical Urgency / Credential Theft Intent
        body = (parsed_data.get("body_plain", "") + " " + parsed_data.get("subject", "")).lower()
        urgency_terms = ["password expiring", "account suspended", "urgent: confidential", "wire instruction", "escrow deposit", "immediate password expiration"]
        found_urgency = [t for t in urgency_terms if t in body]
        if found_urgency:
            pts = 10
            score += pts
            evidence_items.append({
                "id": "EVD-BODY-URGENCY",
                "category": "BODY",
                "title": "High Urgency & Social Engineering Language",
                "description": f"Subject/body leverages social engineering triggers: '{', '.join(found_urgency)}'.",
                "risk_contribution": pts,
                "is_deceptive": False
            })

        # 6. Campaign Correlation Bonus
        if campaign_info:
            pts = 15
            score += pts
            evidence_items.append({
                "id": f"EVD-CMP-{campaign_info.get('id')}",
                "category": "DNS",
                "title": f"Correlated with Active Threat Campaign: {campaign_info.get('name')}",
                "description": f"Matches Campaign DNA ({campaign_info.get('campaign_dna')}) through shared relay/domain infrastructure.",
                "risk_contribution": pts,
                "is_deceptive": True
            })

        # Clamp score between 0 and 100
        final_score = min(max(score, 0), 100)

        # 7. Classification Taxonomy
        if final_score < 25:
            if not parsed_data.get("received_headers") and not parsed_data.get("auth", {}).get("spf", {}).get("status") in ("PASS", "FAIL"):
                threat_class = "UNKNOWN / NEEDS_REVIEW"
            else:
                threat_class = "BENIGN"
        elif any(e.get("category") == "ATTACHMENT" and e.get("risk_contribution", 0) >= 28 for e in evidence_items):
            threat_class = "MALWARE_DELIVERY"
        elif any("BEC" in e.get("title", "") for e in evidence_items):
            threat_class = "BUSINESS_EMAIL_COMPROMISE"
        elif any("Urgency" in e.get("title", "") for e in evidence_items) and final_score >= 70:
            threat_class = "CREDENTIAL_HARVESTING"
        elif final_score >= 60:
            threat_class = "PHISHING"
        else:
            threat_class = "SPAM"

        # Special check: Benign pass vs Insufficient evidence
        if spf.get("status") == "PASS" and dkim.get("status") == "PASS":
            threat_class = "BENIGN"
            final_score = min(final_score, 15)
            threat_conf = 0.95
            evd_conf = 0.92
            infra_conf = 0.88
            evidence_items.append({
                "id": "EVD-AUTH-PASS",
                "category": "AUTH",
                "title": "Cryptographic Authentication Passed",
                "description": "SPF and DKIM cryptographic signatures successfully verified against sender domain.",
                "risk_contribution": 0,
                "is_deceptive": False
            })
        elif len(evidence_items) == 0 and final_score == 0:
            threat_class = "INSUFFICIENT_EVIDENCE"
            threat_conf = 0.30
            evd_conf = 0.25
            infra_conf = 0.20
        else:
            threat_conf = min(0.98, max(0.40, 0.45 + (final_score / 180.0)))
            evd_conf = min(0.99, max(0.50, 0.40 + (len(evidence_items) * 0.12)))
            infra_conf = 0.88 if has_malicious_ip or has_malicious_domain else 0.45

        # 8. Counterfactual Simulation
        counterfactuals = TransparentRiskEngine._generate_counterfactuals(
            current_score=final_score,
            evidence_items=evidence_items
        )

        return {
            "threat_score": final_score,
            "threat_class": threat_class,
            "threat_confidence": round(threat_conf, 2),
            "evidence_confidence": round(evd_conf, 2),
            "infrastructure_confidence": round(infra_conf, 2),
            "evidence_items": evidence_items,
            "counterfactuals": counterfactuals
        }

    @staticmethod
    def _generate_counterfactuals(current_score: int, evidence_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for item in evidence_items:
            pts = item.get("risk_contribution", 0)
            if pts > 0:
                new_s = max(0, current_score - pts)
                results.append({
                    "feature_name": item.get("title"),
                    "current_value": "SUSPICIOUS / DETECTED",
                    "simulated_value": "BENIGN / ALIGNED",
                    "delta_score": -pts,
                    "new_score": new_s,
                    "explanation": f"If '{item.get('title')}' were benign, threat score would decrease from {current_score} to {new_s}."
                })
        return results

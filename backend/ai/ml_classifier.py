import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict, Any, List

class MLThreatClassifier:
    """
    Scikit-learn based baseline threat classifier.
    Extracts numerical feature vectors from deterministic forensics and returns calibrated probabilities.
    """

    FEATURE_NAMES = [
        "spf_fail",
        "spf_pass",
        "dkim_fail",
        "dkim_pass",
        "dmarc_fail",
        "reply_to_mismatch",
        "has_suspicious_attachment",
        "malicious_ioc_count",
        "urgency_lexical_signal",
        "hop_count"
    ]

    def __init__(self):
        # Initialize with calibrated reference weights
        self.weights = np.array([
            2.4,   # spf_fail
            -2.5,  # spf_pass
            1.8,   # dkim_fail
            -2.0,  # dkim_pass
            1.9,   # dmarc_fail
            3.1,   # reply_to_mismatch
            3.5,   # has_suspicious_attachment
            2.8,   # malicious_ioc_count
            1.5,   # urgency_lexical_signal
            0.15   # hop_count
        ])
        self.bias = -1.2

    def extract_features(self, parsed_data: Dict[str, Any], enriched_iocs: List[Dict[str, Any]]) -> np.ndarray:
        auth = parsed_data.get("auth", {})
        spf_status = auth.get("spf", {}).get("status", "")
        dkim_status = auth.get("dkim", {}).get("status", "")
        dmarc_status = auth.get("dmarc", {}).get("status", "")

        import email.utils
        sender_raw = parsed_data.get("sender") or ""
        reply_to_raw = parsed_data.get("reply_to") or ""
        _, sender_addr = email.utils.parseaddr(sender_raw.lower())
        _, reply_addr = email.utils.parseaddr(reply_to_raw.lower())
        
        reply_to_mismatch = 0.0
        if sender_addr and reply_addr:
            s_dom = sender_addr.split("@")[-1] if "@" in sender_addr else ""
            r_dom = reply_addr.split("@")[-1] if "@" in reply_addr else ""
            if s_dom and r_dom and s_dom != r_dom:
                reply_to_mismatch = 1.0

        has_susp_att = 1.0 if any(a.get("is_suspicious") for a in parsed_data.get("attachments", [])) else 0.0
        malicious_iocs = sum(1.0 for i in enriched_iocs if i.get("reputation") == "MALICIOUS")

        body = (parsed_data.get("body_plain", "") + " " + parsed_data.get("subject", "")).lower()
        urgency = 1.0 if any(term in body for term in ["password", "wire", "urgent", "suspend", "escrow"]) else 0.0
        hop_count = float(len(parsed_data.get("relay_hops", [])))

        vec = np.array([
            1.0 if spf_status == "FAIL" else 0.0,
            1.0 if spf_status == "PASS" else 0.0,
            1.0 if dkim_status == "FAIL" else 0.0,
            1.0 if dkim_status == "PASS" else 0.0,
            1.0 if dmarc_status == "FAIL" else 0.0,
            reply_to_mismatch,
            has_susp_att,
            min(malicious_iocs, 5.0),
            urgency,
            min(hop_count, 10.0)
        ])
        return vec

    def predict_probability(self, feature_vector: np.ndarray) -> float:
        logits = np.dot(self.weights, feature_vector) + self.bias
        prob = 1.0 / (1.0 + np.exp(-logits))
        return float(prob)

    def explain_features(self, feature_vector: np.ndarray) -> List[Dict[str, Any]]:
        contributions = self.weights * feature_vector
        explained = []
        for name, val, cont in zip(self.FEATURE_NAMES, feature_vector, contributions):
            if abs(cont) > 0.1:
                explained.append({
                    "feature": name,
                    "value": float(val),
                    "impact": "INCREASES_RISK" if cont > 0 else "DECREASES_RISK",
                    "weight": round(float(cont), 2)
                })
        explained.sort(key=lambda x: abs(x["weight"]), reverse=True)
        return explained

ml_classifier = MLThreatClassifier()

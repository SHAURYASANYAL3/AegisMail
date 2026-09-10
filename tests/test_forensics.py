import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.forensics.email_parser import SafeEmailParser
from backend.forensics.auth import EmailAuthAnalyzer
from backend.forensics.headers import HeaderHopAnalyzer
from backend.forensics.ioc_extractor import IOCExtractor
from backend.risk.engine import TransparentRiskEngine
from backend.intel.manager import intel_manager
from backend.response.engine import IncidentResponseEngine

client = TestClient(app)

def test_health_check():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["offline_ready"] is True

def test_auth_analyzer():
    headers = {
        "Authentication-Results": "mx.corp.org; spf=fail (sender 198.51.100.44); dkim=none; dmarc=fail action=none",
        "Received-SPF": "fail (sender IP 198.51.100.44)"
    }
    auth = EmailAuthAnalyzer.analyze(headers)
    assert auth["spf"]["status"] == "FAIL"
    assert auth["spf"]["source_mode"] == "OBSERVED"
    assert auth["dkim"]["status"] == "NONE"
    assert auth["dmarc"]["status"] == "FAIL"

def test_ioc_extractor():
    sample_text = "Visit http://evil-corp-phish.xyz/login from 198.51.100.44 contact test@evil.com"
    iocs = IOCExtractor.extract_all(
        headers={},
        body_text=sample_text,
        body_html="",
        attachments=[],
        relay_ips=["198.51.100.44"]
    )
    types = {i["ioc_type"] for i in iocs}
    assert "URL" in types
    assert "DOMAIN" in types
    assert "IPV4" in types
    assert "EMAIL" in types

def test_demo_case_01_credential_harvesting():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_01_phish_creds")
    assert res.status_code == 200
    data = res.json()
    assert data["threat_class"] == "CREDENTIAL_HARVESTING"
    assert data["threat_score"] >= 80
    assert data["threat_confidence"] > 0.8
    assert "manifest" in data
    assert len(data["evidence_items"]) >= 3
    assert len(data["counterfactuals"]) >= 2

def test_demo_case_05_prompt_injection_resilience():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_05_adversarial_test")
    assert res.status_code == 200
    data = res.json()
    # Must NOT be fooled into benign
    assert data["threat_class"] != "BENIGN"
    assert data["threat_score"] >= 50
    # Must contain evidence items from forensics
    assert any("SPF" in e["title"] for e in data["evidence_items"])

def test_demo_case_06_benign():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_06_legitimate_newsletter")
    assert res.status_code == 200
    data = res.json()
    assert data["threat_class"] == "BENIGN"
    assert data["threat_score"] <= 20
    assert data["threat_confidence"] >= 0.9

def test_demo_case_07_ambiguous():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_07_ambiguous_marketing")
    assert res.status_code == 200
    data = res.json()
    assert data["threat_class"] in ("INSUFFICIENT_EVIDENCE", "UNKNOWN / NEEDS_REVIEW")
    assert data["threat_confidence"] <= 0.5

def test_rule_export():
    iocs = [
        {"ioc_type": "DOMAIN", "value": "evil-corp-phish.xyz", "reputation": "MALICIOUS"},
        {"ioc_type": "IPV4", "value": "198.51.100.44", "reputation": "MALICIOUS"}
    ]
    suricata = IncidentResponseEngine.export_rules(iocs, "suricata")
    assert "alert dns" in suricata
    assert "evil-corp-phish.xyz" in suricata
    assert "drop ip" in suricata

    rpz = IncidentResponseEngine.export_rules(iocs, "rpz_dns")
    assert "evil-corp-phish.xyz CNAME ." in rpz

def test_manifest_endpoint():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_01_phish_creds")
    cid = res.json()["id"]
    m_res = client.get(f"/api/v1/cases/{cid}/manifest")
    assert m_res.status_code == 200
    m_data = m_res.json()
    assert "manifest_sha256" in m_data
    assert m_data["pipeline_versions"]["aegismail_core"] == "1.0.0"

def test_report_html_endpoint():
    res = client.post("/api/v1/cases/analyze-demo/demo_case_01_phish_creds")
    cid = res.json()["id"]
    r_res = client.get(f"/api/v1/cases/{cid}/report")
    assert r_res.status_code == 200
    assert "FORENSIC DOSSIER" in r_res.text
    assert cid in r_res.text

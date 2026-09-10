from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json

from backend.config import settings
from backend.models.database import engine, Base, get_db
from backend.models.entities import CaseModel, EvidenceModel, IOCModel, TimelineModel, CampaignModel
from backend.models.schemas import (
    CaseSummarySchema, CaseDetailSchema, CampaignDetailSchema
)
from backend.pipeline import AnalysisPipeline
from backend.correlation.engine import KNOWN_CAMPAIGNS
from backend.response.engine import IncidentResponseEngine
from backend.reports.generator import ForensicReportGenerator

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    with next(get_db()) as db:
        for c in KNOWN_CAMPAIGNS:
            existing = db.query(CampaignModel).filter(CampaignModel.id == c["id"]).first()
            if not existing:
                camp = CampaignModel(
                    id=c["id"],
                    name=c["name"],
                    campaign_dna=c["campaign_dna"],
                    primary_threat=c["primary_threat"],
                    summary=c["summary"]
                )
                db.add(camp)
        db.commit()
    yield

app = FastAPI(
    title="AegisMail API",
    description="Evidence-Correlated AI Email Digital Forensics, Threat Intelligence, and Incident Response Platform",
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.demo_mode,
        "offline_ready": True,
        "database": "connected"
    }

@app.post("/api/v1/cases/upload")
async def upload_case(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        content = await file.read()
        filename = file.filename or "uploaded_artifact.eml"
        result = AnalysisPipeline.process_eml(
            raw_bytes=content,
            filename=filename,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze email artifact: {str(e)}")

@app.post("/api/v1/cases/analyze-demo/{demo_name}")
def analyze_demo_case(demo_name: str, db: Session = Depends(get_db)):
    demo_path = os.path.join("data", "demo", f"{demo_name}.eml")
    if not os.path.exists(demo_path):
        raise HTTPException(status_code=404, detail=f"Demo fixture '{demo_name}' not found.")
    
    with open(demo_path, "rb") as f:
        content = f.read()

    result = AnalysisPipeline.process_eml(
        raw_bytes=content,
        filename=f"{demo_name}.eml",
        db=db,
        case_id=f"CASE-DEMO-{demo_name.upper()[:14]}"
    )
    return result

@app.get("/api/v1/cases")
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(CaseModel).order_by(CaseModel.created_at.desc()).all()
    results = []
    for c in cases:
        results.append({
            "id": c.id,
            "sha256_hash": c.sha256_hash,
            "original_filename": c.original_filename,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "sender": c.sender,
            "subject": c.subject,
            "threat_class": c.threat_class,
            "threat_score": c.threat_score,
            "threat_confidence": c.threat_confidence,
            "evidence_confidence": c.evidence_confidence,
            "infrastructure_confidence": c.infrastructure_confidence,
            "campaign_id": c.campaign_id,
            "status": c.status
        })
    return results

@app.get("/api/v1/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    c = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    evidence_items = [
        {
            "id": e.id,
            "category": e.category,
            "title": e.title,
            "description": e.description,
            "risk_contribution": e.risk_contribution,
            "is_deceptive": e.is_deceptive,
            "sha256": e.sha256
        }
        for e in c.evidence_items
    ]

    iocs = [
        {
            "id": i.id,
            "ioc_type": i.ioc_type,
            "value": i.value,
            "normalized_value": i.normalized_value,
            "reputation": i.reputation,
            "asn": i.asn,
            "asn_org": i.asn_org,
            "country": i.country,
            "city": i.city,
            "latitude": i.latitude,
            "longitude": i.longitude,
            "confidence": i.confidence
        }
        for i in c.iocs
    ]

    timeline = [
        {
            "id": t.id,
            "timestamp": t.timestamp.isoformat() if t.timestamp else "",
            "event_type": t.event_type,
            "actor": t.actor,
            "description": t.description
        }
        for t in c.timeline_events
    ]

    campaign_name = c.campaign.name if c.campaign else None
    campaign_dna = c.campaign.campaign_dna if c.campaign else None

    # Reconstruct graph from stored entities
    from backend.graph.builder import EvidenceGraphBuilder
    parsed_dummy = {
        "sender": c.sender,
        "reply_to": c.reply_to,
        "relay_hops": json.loads(c.relay_hops_json or "[]")
    }
    camp_dummy = {"id": c.campaign_id, "name": campaign_name, "campaign_dna": campaign_dna, "confidence": 0.9} if c.campaign_id else None
    graph = EvidenceGraphBuilder.build_case_graph(c.id, parsed_dummy, iocs, camp_dummy)

    return {
        "id": c.id,
        "sha256_hash": c.sha256_hash,
        "original_filename": c.original_filename,
        "created_at": c.created_at.isoformat() if c.created_at else "",
        "sender": c.sender,
        "recipient": c.recipient,
        "subject": c.subject,
        "date_header": c.date_header,
        "message_id": c.message_id,
        "reply_to": c.reply_to,
        "return_path": c.return_path,
        "spf_status": c.spf_status,
        "dkim_status": c.dkim_status,
        "dmarc_status": c.dmarc_status,
        "threat_class": c.threat_class,
        "threat_score": c.threat_score,
        "threat_confidence": c.threat_confidence,
        "evidence_confidence": c.evidence_confidence,
        "infrastructure_confidence": c.infrastructure_confidence,
        "campaign_id": c.campaign_id,
        "campaign_name": campaign_name,
        "campaign_dna": campaign_dna,
        "status": c.status,
        "evidence_items": evidence_items,
        "iocs": iocs,
        "relay_hops": json.loads(c.relay_hops_json or "[]"),
        "timeline": timeline,
        "graph": graph,
        "counterfactuals": json.loads(c.counterfactuals_json or "[]"),
        "recommended_actions": json.loads(c.response_actions_json or "[]"),
        "manifest": json.loads(c.manifest_json or "{}")
    }

@app.get("/api/v1/cases/{case_id}/manifest")
def get_manifest(case_id: str, db: Session = Depends(get_db)):
    c = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return json.loads(c.manifest_json or "{}")

@app.get("/api/v1/cases/{case_id}/report", response_class=HTMLResponse)
def get_html_report(case_id: str, redact_pii: bool = False, db: Session = Depends(get_db)):
    case_data = get_case(case_id, db)
    html = ForensicReportGenerator.generate_html_report(case_data, redact_pii=redact_pii)
    return html

@app.post("/api/v1/cases/{case_id}/actions/export-rules")
def export_case_rules(case_id: str, format: str = Query("suricata"), db: Session = Depends(get_db)):
    case_data = get_case(case_id, db)
    rules_text = IncidentResponseEngine.export_rules(case_data.get("iocs", []), rule_format=format)
    return {"format": format, "rules": rules_text}

@app.get("/api/v1/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(CampaignModel).all()
    results = []
    for camp in campaigns:
        case_ids = [c.id for c in camp.cases]
        results.append({
            "id": camp.id,
            "name": camp.name,
            "campaign_dna": camp.campaign_dna,
            "first_seen": camp.first_seen.isoformat() if camp.first_seen else "",
            "last_seen": camp.last_seen.isoformat() if camp.last_seen else "",
            "primary_threat": camp.primary_threat,
            "summary": camp.summary,
            "case_ids": case_ids,
            "case_count": len(case_ids)
        })
    return results

import uuid
from datetime import datetime, timezone
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.forensics.email_parser import SafeEmailParser
from backend.intel.manager import intel_manager
from backend.correlation.engine import CampaignCorrelationEngine, KNOWN_CAMPAIGNS
from backend.risk.engine import TransparentRiskEngine
from backend.graph.builder import EvidenceGraphBuilder
from backend.response.engine import IncidentResponseEngine
from backend.ai.explainer import GroundedExplainer
from backend.reports.generator import ForensicReportGenerator
from backend.models.entities import (
    CaseModel, EvidenceModel, IOCModel, TimelineModel, CampaignModel, GraphRelationshipModel
)

class AnalysisPipeline:
    """
    End-to-End Forensics & Correlation Execution Pipeline.
    Turns raw EML into a fully analyzed, evidence-correlated case with cryptographic manifest.
    """

    @staticmethod
    def process_eml(raw_bytes: bytes, filename: str, db: Session, case_id: Optional[str] = None) -> Dict[str, Any]:
        cid = case_id or f"CASE-{datetime.now(timezone.utc).strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
        
        # 1. Forensic Parsing
        parsed = SafeEmailParser.parse_eml_bytes(raw_bytes, filename)
        
        # 2. IOC Enrichment via Local/Curated Store
        enriched_iocs = intel_manager.enrich_iocs(parsed.get("iocs", []))

        # 3. Campaign Matching
        campaign_match = CampaignCorrelationEngine.match_campaign(enriched_iocs, parsed)

        # 4. Transparent Risk Scoring & Counterfactuals
        risk_result = TransparentRiskEngine.evaluate(parsed, enriched_iocs, campaign_match)

        # 5. Evidence Graph Generation
        graph = EvidenceGraphBuilder.build_case_graph(cid, parsed, enriched_iocs, campaign_match)

        # 6. Response Playbook
        case_temp_dict = {
            "id": cid,
            "sha256_hash": parsed["sha256"],
            "threat_class": risk_result["threat_class"],
            "threat_score": risk_result["threat_score"],
            "sender": parsed["sender"],
            "message_id": parsed["message_id"],
            "iocs": enriched_iocs
        }
        playbook = IncidentResponseEngine.generate_playbook(case_temp_dict)

        # 7. Grounded Explanation Narrative
        case_temp_dict["evidence_items"] = risk_result["evidence_items"]
        case_temp_dict["threat_confidence"] = risk_result["threat_confidence"]
        case_temp_dict["evidence_confidence"] = risk_result["evidence_confidence"]
        case_temp_dict["infrastructure_confidence"] = risk_result["infrastructure_confidence"]
        case_temp_dict["auth"] = parsed["auth"]
        case_temp_dict["campaign_info"] = campaign_match
        ai_summary = GroundedExplainer.generate_narrative(case_temp_dict)

        # 8. Investigation Timeline Events
        now_iso = datetime.now(timezone.utc).isoformat()
        timeline = [
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "ARTIFACT_INGESTED", "actor": "SYSTEM_INGEST", "description": f"Raw email artifact received ({parsed['byte_size']} bytes). Calculated SHA-256: {parsed['sha256']}"},
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "MIME_PARSED", "actor": "SYSTEM_PARSER", "description": f"Extracted MIME structure, {len(parsed.get('attachments', []))} attachments, {len(parsed.get('relay_hops', []))} relay hops."},
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "AUTH_VERIFIED", "actor": "AUTH_ANALYZER", "description": f"Authentication evaluated: SPF={parsed['auth']['spf']['status']}, DKIM={parsed['auth']['dkim']['status']}, DMARC={parsed['auth']['dmarc']['status']}."},
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "IOCS_EXTRACTED", "actor": "IOC_EXTRACTOR", "description": f"Extracted and normalized {len(enriched_iocs)} indicators of compromise."},
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "INTEL_RESOLVED", "actor": "THREAT_INTEL", "description": "Resolved ASN, GeoIP, and threat reputation via local intelligence store."},
            {"id": f"TL-{uuid.uuid4().hex[:6]}", "timestamp": now_iso, "event_type": "RISK_EVALUATED", "actor": "RISK_ENGINE", "description": f"Assigned verdict: {risk_result['threat_class']} (Score: {risk_result['threat_score']}/100, Threat Confidence: {int(risk_result['threat_confidence']*100)}%)."}
        ]

        if campaign_match:
            timeline.append({
                "id": f"TL-{uuid.uuid4().hex[:6]}",
                "timestamp": now_iso,
                "event_type": "CAMPAIGN_LINKED",
                "actor": "CORRELATION_ENGINE",
                "description": f"Observed infrastructure match with Campaign '{campaign_match['name']}' (DNA: {campaign_match['campaign_dna']})."
            })

        # 9. Cryptographic Manifest
        case_temp_dict["timeline"] = timeline
        case_temp_dict["original_filename"] = filename
        manifest = ForensicReportGenerator.generate_manifest(case_temp_dict)

        # 10. Persist in Database
        case_record = CaseModel(
            id=cid,
            sha256_hash=parsed["sha256"],
            original_filename=filename,
            sender=parsed["sender"],
            recipient=parsed["recipient"],
            subject=parsed["subject"],
            date_header=parsed["date_header"],
            message_id=parsed["message_id"],
            reply_to=parsed["reply_to"],
            return_path=parsed["return_path"],
            spf_status=parsed["auth"]["spf"]["status"],
            dkim_status=parsed["auth"]["dkim"]["status"],
            dmarc_status=parsed["auth"]["dmarc"]["status"],
            threat_class=risk_result["threat_class"],
            threat_score=risk_result["threat_score"],
            threat_confidence=risk_result["threat_confidence"],
            evidence_confidence=risk_result["evidence_confidence"],
            infrastructure_confidence=risk_result["infrastructure_confidence"],
            campaign_id=campaign_match["id"] if campaign_match else None,
            status="INVESTIGATING",
            raw_headers_json=json.dumps(parsed["headers"]),
            relay_hops_json=json.dumps(parsed["relay_hops"]),
            counterfactuals_json=json.dumps(risk_result["counterfactuals"]),
            response_actions_json=json.dumps(playbook),
            manifest_json=json.dumps(manifest)
        )
        db.merge(case_record)

        # Persist Evidence Items
        for ev in risk_result["evidence_items"]:
            ev_record = EvidenceModel(
                id=f"{cid}-{ev['id']}",
                case_id=cid,
                category=ev["category"],
                title=ev["title"],
                description=ev["description"],
                risk_contribution=ev["risk_contribution"],
                is_deceptive=ev["is_deceptive"],
                sha256=ev.get("sha256")
            )
            db.merge(ev_record)

        # Persist IOCs
        for idx, ioc in enumerate(enriched_iocs):
            ioc_record = IOCModel(
                id=f"{cid}-IOC-{idx}",
                case_id=cid,
                ioc_type=ioc["ioc_type"],
                value=ioc["value"],
                normalized_value=ioc["normalized_value"],
                reputation=ioc["reputation"],
                asn=ioc.get("asn"),
                asn_org=ioc.get("asn_org"),
                country=ioc.get("country"),
                city=ioc.get("city"),
                latitude=ioc.get("latitude"),
                longitude=ioc.get("longitude"),
                confidence=ioc.get("confidence", 0.5)
            )
            db.merge(ioc_record)

        # Persist Timeline
        for tl in timeline:
            tl_record = TimelineModel(
                id=tl["id"],
                case_id=cid,
                event_type=tl["event_type"],
                actor=tl["actor"],
                description=tl["description"]
            )
            db.merge(tl_record)

        db.commit()

        # Build full JSON response object
        return {
            "id": cid,
            "sha256_hash": parsed["sha256"],
            "original_filename": filename,
            "created_at": now_iso,
            "sender": parsed["sender"],
            "recipient": parsed["recipient"],
            "subject": parsed["subject"],
            "date_header": parsed["date_header"],
            "message_id": parsed["message_id"],
            "reply_to": parsed["reply_to"],
            "return_path": parsed["return_path"],
            "spf_status": parsed["auth"]["spf"]["status"],
            "dkim_status": parsed["auth"]["dkim"]["status"],
            "dmarc_status": parsed["auth"]["dmarc"]["status"],
            "threat_class": risk_result["threat_class"],
            "threat_score": risk_result["threat_score"],
            "threat_confidence": risk_result["threat_confidence"],
            "evidence_confidence": risk_result["evidence_confidence"],
            "infrastructure_confidence": risk_result["infrastructure_confidence"],
            "campaign_id": campaign_match["id"] if campaign_match else None,
            "campaign_name": campaign_match["name"] if campaign_match else None,
            "campaign_dna": campaign_match["campaign_dna"] if campaign_match else None,
            "status": "INVESTIGATING",
            "evidence_items": risk_result["evidence_items"],
            "iocs": enriched_iocs,
            "relay_hops": parsed["relay_hops"],
            "timeline": timeline,
            "graph": graph,
            "counterfactuals": risk_result["counterfactuals"],
            "recommended_actions": playbook,
            "ai_summary": ai_summary,
            "body_text_sanitized": parsed["body_plain"],
            "body_html_sanitized": parsed["body_html_sanitized"],
            "manifest": manifest
        }

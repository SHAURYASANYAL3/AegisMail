from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from backend.models.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CaseModel(Base):
    __tablename__ = "cases"

    id = Column(String(64), primary_key=True, index=True)
    sha256_hash = Column(String(64), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    
    sender = Column(String(255), nullable=True)
    recipient = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    date_header = Column(String(255), nullable=True)
    message_id = Column(String(255), nullable=True)
    reply_to = Column(String(255), nullable=True)
    return_path = Column(String(255), nullable=True)
    
    # Forensic Status
    spf_status = Column(String(32), default="UNKNOWN")
    dkim_status = Column(String(32), default="UNKNOWN")
    dmarc_status = Column(String(32), default="UNKNOWN")
    
    # Threat & Confidence
    threat_class = Column(String(64), default="UNKNOWN / NEEDS_REVIEW")
    threat_score = Column(Integer, default=0)
    threat_confidence = Column(Float, default=0.5)
    evidence_confidence = Column(Float, default=0.5)
    infrastructure_confidence = Column(Float, default=0.5)
    
    campaign_id = Column(String(64), ForeignKey("campaigns.id"), nullable=True)
    status = Column(String(32), default="INVESTIGATING")
    
    # Serialized JSON blobs for deep attributes
    raw_headers_json = Column(Text, default="{}")
    relay_hops_json = Column(Text, default="[]")
    counterfactuals_json = Column(Text, default="[]")
    response_actions_json = Column(Text, default="[]")
    manifest_json = Column(Text, default="{}")

    # Relationships
    evidence_items = relationship("EvidenceModel", back_populates="case", cascade="all, delete-orphan")
    iocs = relationship("IOCModel", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineModel", back_populates="case", cascade="all, delete-orphan")
    campaign = relationship("CampaignModel", back_populates="cases")

class EvidenceModel(Base):
    __tablename__ = "evidence_items"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    category = Column(String(32), nullable=False) # HEADER, BODY, URL, ATTACHMENT, AUTH, DNS
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    raw_content = Column(Text, nullable=True)
    sha256 = Column(String(64), nullable=True)
    risk_contribution = Column(Integer, default=0)
    is_deceptive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("CaseModel", back_populates="evidence_items")

class IOCModel(Base):
    __tablename__ = "iocs"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    ioc_type = Column(String(32), nullable=False) # IPV4, IPV6, DOMAIN, URL, EMAIL, SHA256
    value = Column(String(500), nullable=False)
    normalized_value = Column(String(500), nullable=False, index=True)
    reputation = Column(String(32), default="UNKNOWN")
    asn = Column(String(64), nullable=True)
    asn_org = Column(String(255), nullable=True)
    country = Column(String(64), nullable=True)
    city = Column(String(64), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, default=0.5)
    source_evidence_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("CaseModel", back_populates="iocs")

class TimelineModel(Base):
    __tablename__ = "timeline_events"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=utc_now)
    event_type = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False) # SYSTEM_PARSER, RISK_ENGINE, ANALYST
    description = Column(Text, nullable=False)
    evidence_ref = Column(String(64), nullable=True)

    case = relationship("CaseModel", back_populates="timeline_events")

class CampaignModel(Base):
    __tablename__ = "campaigns"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    campaign_dna = Column(String(64), nullable=False)
    first_seen = Column(DateTime, default=utc_now)
    last_seen = Column(DateTime, default=utc_now)
    primary_threat = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)

    cases = relationship("CaseModel", back_populates="campaign")

class GraphRelationshipModel(Base):
    __tablename__ = "graph_relationships"

    id = Column(String(64), primary_key=True, index=True)
    source_node = Column(String(255), nullable=False, index=True)
    source_type = Column(String(64), nullable=False)
    relationship_type = Column(String(64), nullable=False) # SENT_FROM, REPLY_TO, RESOLVES_TO, HOSTED_ON, etc.
    target_node = Column(String(255), nullable=False, index=True)
    target_type = Column(String(64), nullable=False)
    evidence_id = Column(String(64), nullable=True)
    confidence = Column(Float, default=0.8)
    case_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)

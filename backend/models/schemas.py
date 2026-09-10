from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EvidenceItemSchema(BaseModel):
    id: str
    category: str
    title: str
    description: str
    raw_content: Optional[str] = None
    sha256: Optional[str] = None
    risk_contribution: int = 0
    is_deceptive: bool = False

class IOCSchema(BaseModel):
    id: str
    ioc_type: str
    value: str
    normalized_value: str
    reputation: str
    asn: Optional[str] = None
    asn_org: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: float
    source_evidence_id: Optional[str] = None

class RelayHopSchema(BaseModel):
    hop_index: int
    by_host: Optional[str] = None
    from_host: Optional[str] = None
    sender_ip: Optional[str] = None
    protocol: Optional[str] = None
    timestamp: Optional[str] = None
    delay_seconds: Optional[int] = None
    is_suspicious: bool = False

class TimelineEventSchema(BaseModel):
    id: str
    timestamp: str
    event_type: str
    actor: str
    description: str
    evidence_ref: Optional[str] = None

class GraphNodeSchema(BaseModel):
    id: str
    label: str
    type: str
    threat_status: Optional[str] = "UNKNOWN"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    relationship: str
    confidence: float
    evidence_id: Optional[str] = None

class CytoscapeGraphSchema(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class CounterfactualItemSchema(BaseModel):
    feature_name: str
    current_value: str
    simulated_value: str
    delta_score: int
    new_score: int
    explanation: str

class ResponseActionSchema(BaseModel):
    id: str
    action_type: str # QUARANTINE, BLOCK_DOMAIN, BLOCK_IP, PRESERVE_EVIDENCE
    target: str
    priority: str # HIGH, MEDIUM, LOW
    requires_human_approval: bool
    status: str # RECOMMENDED, APPROVED, EXECUTED
    rationale: str

class CaseDetailSchema(BaseModel):
    id: str
    sha256_hash: str
    original_filename: str
    created_at: str
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    date_header: Optional[str] = None
    message_id: Optional[str] = None
    reply_to: Optional[str] = None
    return_path: Optional[str] = None
    
    spf_status: str
    dkim_status: str
    dmarc_status: str
    
    threat_class: str
    threat_score: int
    threat_confidence: float
    evidence_confidence: float
    infrastructure_confidence: float
    
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    campaign_dna: Optional[str] = None
    status: str
    
    evidence_items: List[EvidenceItemSchema] = Field(default_factory=list)
    iocs: List[IOCSchema] = Field(default_factory=list)
    relay_hops: List[RelayHopSchema] = Field(default_factory=list)
    timeline: List[TimelineEventSchema] = Field(default_factory=list)
    graph: CytoscapeGraphSchema
    counterfactuals: List[CounterfactualItemSchema] = Field(default_factory=list)
    recommended_actions: List[ResponseActionSchema] = Field(default_factory=list)
    
    ai_summary: Optional[str] = None
    body_text_sanitized: Optional[str] = None
    body_html_sanitized: Optional[str] = None

class CaseSummarySchema(BaseModel):
    id: str
    sha256_hash: str
    original_filename: str
    created_at: str
    sender: Optional[str] = None
    subject: Optional[str] = None
    threat_class: str
    threat_score: int
    threat_confidence: float
    evidence_confidence: float
    infrastructure_confidence: float
    campaign_id: Optional[str] = None
    status: str

class CampaignDetailSchema(BaseModel):
    id: str
    name: str
    campaign_dna: str
    first_seen: str
    last_seen: str
    primary_threat: str
    summary: Optional[str] = None
    case_ids: List[str] = Field(default_factory=list)
    shared_infrastructure: List[str] = Field(default_factory=list)

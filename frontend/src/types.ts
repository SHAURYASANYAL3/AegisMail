export interface EvidenceItem {
  id: string;
  category: 'HEADER' | 'BODY' | 'URL' | 'ATTACHMENT' | 'AUTH' | 'DNS';
  title: string;
  description: string;
  risk_contribution: number;
  is_deceptive: boolean;
  sha256?: string;
}

export interface IOC {
  id: string;
  ioc_type: 'IPV4' | 'IPV6' | 'DOMAIN' | 'URL' | 'EMAIL' | 'SHA256';
  value: string;
  normalized_value: string;
  reputation: 'BENIGN' | 'SUSPICIOUS' | 'MALICIOUS' | 'UNKNOWN';
  asn?: string;
  asn_org?: string;
  country?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  confidence: number;
}

export interface RelayHop {
  hop_index: number;
  by_host?: string;
  from_host?: string;
  sender_ip?: string;
  protocol?: string;
  timestamp?: string;
  delay_seconds?: number;
  is_suspicious: boolean;
  raw?: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  event_type: string;
  actor: string;
  description: string;
}

export interface CytoscapeElement {
  data: {
    id: string;
    label?: string;
    type?: string;
    threat_status?: string;
    source?: string;
    target?: string;
    relationship?: string;
    confidence?: number;
    [key: string]: any;
  };
}

export interface CytoscapeGraph {
  nodes: CytoscapeElement[];
  edges: CytoscapeElement[];
}

export interface Counterfactual {
  feature_name: string;
  current_value: string;
  simulated_value: string;
  delta_score: number;
  new_score: number;
  explanation: string;
}

export interface ResponseAction {
  id: string;
  action_type: string;
  target: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  requires_human_approval: boolean;
  status: string;
  rationale: string;
}

export interface CaseDetail {
  id: string;
  sha256_hash: string;
  original_filename: string;
  created_at: string;
  sender?: string;
  recipient?: string;
  subject?: string;
  date_header?: string;
  message_id?: string;
  reply_to?: string;
  return_path?: string;

  spf_status: string;
  dkim_status: string;
  dmarc_status: string;

  threat_class: string;
  threat_score: number;
  threat_confidence: number;
  evidence_confidence: number;
  infrastructure_confidence: number;

  campaign_id?: string;
  campaign_name?: string;
  campaign_dna?: string;
  status: string;

  evidence_items: EvidenceItem[];
  iocs: IOC[];
  relay_hops: RelayHop[];
  timeline: TimelineEvent[];
  graph: CytoscapeGraph;
  counterfactuals: Counterfactual[];
  recommended_actions: ResponseAction[];

  ai_summary?: string;
  body_text_sanitized?: string;
  body_html_sanitized?: string;
  raw_headers_json?: string;
  manifest?: Record<string, any>;
}

export interface CampaignSummary {
  id: string;
  name: string;
  campaign_dna: string;
  first_seen: string;
  last_seen: string;
  primary_threat: string;
  summary?: string;
  case_ids: string[];
  case_count: number;
}

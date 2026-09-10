import networkx as nx
from typing import Dict, Any, List

class EvidenceGraphBuilder:
    """
    Constructs an evidence-backed directed graph connecting:
    Case -> Sender -> Relay IP -> ASN -> Payload URL -> Payload Domain -> Campaign
    Outputs Cytoscape.js compatible data structure.
    """

    @staticmethod
    def build_case_graph(
        case_id: str,
        parsed_data: Dict[str, Any],
        enriched_iocs: List[Dict[str, Any]],
        campaign_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        G = nx.MultiDiGraph()

        # 1. Root Node: Case
        G.add_node(case_id, label=case_id, type="CASE", threat_status="INVESTIGATION", score=0)

        sender = parsed_data.get("sender") or "unknown@sender.local"
        sender_node = f"SENDER:{sender}"
        G.add_node(sender_node, label=sender, type="SENDER", threat_status="OBSERVED")
        G.add_edge(case_id, sender_node, id=f"e_{case_id}_{sender_node}", relationship="RECEIVED_FROM", confidence=1.0)

        # 2. Reply-To Deception check
        reply_to = parsed_data.get("reply_to")
        if reply_to and reply_to != sender:
            reply_node = f"REPLY_TO:{reply_to}"
            G.add_node(reply_node, label=reply_to, type="REPLY_TO", threat_status="SUSPICIOUS")
            G.add_edge(sender_node, reply_node, id=f"e_reply_mismatch", relationship="DECEPTIVE_REPLY_TO", confidence=0.95)

        # 3. Relay Hops and Originating IP
        hops = parsed_data.get("relay_hops", [])
        for hop in hops:
            ip = hop.get("sender_ip")
            if ip:
                ip_node = f"IP:{ip}"
                is_susp = hop.get("is_suspicious", False)
                threat = "MALICIOUS" if is_susp else "OBSERVED"
                G.add_node(ip_node, label=ip, type="RELAY_IP", threat_status=threat)
                G.add_edge(case_id, ip_node, id=f"e_relay_{hop['hop_index']}", relationship="RELAYED_THROUGH", confidence=0.99)

        # 4. Enriched IOCs (URLs, Domains, ASN, Hashes)
        for ioc in enriched_iocs:
            ioc_type = ioc.get("ioc_type")
            val = ioc.get("value")
            rep = ioc.get("reputation", "UNKNOWN")
            conf = ioc.get("confidence", 0.5)

            if ioc_type == "URL":
                u_node = f"URL:{val}"
                G.add_node(u_node, label=val[:35] + ("..." if len(val) > 35 else ""), type="URL", threat_status=rep, full_url=val)
                G.add_edge(case_id, u_node, id=f"e_url_{hash(val)}", relationship="CONTAINS_URL", confidence=1.0)

                # Link URL to its Domain
                dom = ioc.get("domain")
                if dom:
                    d_node = f"DOMAIN:{dom}"
                    if not G.has_node(d_node):
                        G.add_node(d_node, label=dom, type="DOMAIN", threat_status=rep)
                    G.add_edge(u_node, d_node, id=f"e_resolves_{hash(dom)}", relationship="HOSTED_ON", confidence=0.95)

            elif ioc_type == "DOMAIN":
                d_node = f"DOMAIN:{val}"
                if not G.has_node(d_node):
                    G.add_node(d_node, label=val, type="DOMAIN", threat_status=rep)
                G.add_edge(case_id, d_node, id=f"e_dom_{hash(val)}", relationship="REFERENCES_DOMAIN", confidence=0.90)

                # Link domain to resolved IPs if known
                for res_ip in ioc.get("resolved_ips", []):
                    ip_node = f"IP:{res_ip}"
                    if not G.has_node(ip_node):
                        G.add_node(ip_node, label=res_ip, type="RESOLVED_IP", threat_status=rep)
                    G.add_edge(d_node, ip_node, id=f"e_resolves_ip_{hash(res_ip)}", relationship="RESOLVES_TO", confidence=0.95)

                # Link domain to nameservers
                for ns in ioc.get("nameservers", []):
                    ns_node = f"NAMESERVER:{ns}"
                    if not G.has_node(ns_node):
                        G.add_node(ns_node, label=ns, type="NAMESERVER", threat_status="SUSPICIOUS")
                    G.add_edge(d_node, ns_node, id=f"e_ns_{hash(ns)}", relationship="DELEGATED_TO", confidence=0.90)

            elif ioc_type == "IPV4":
                ip_node = f"IP:{val}"
                if not G.has_node(ip_node):
                    G.add_node(ip_node, label=val, type="IPV4", threat_status=rep)

                asn = ioc.get("asn")
                if asn:
                    asn_node = f"ASN:{asn}"
                    if not G.has_node(asn_node):
                        G.add_node(asn_node, label=f"{asn} ({ioc.get('asn_org', '')})", type="ASN", threat_status="OBSERVED")
                    G.add_edge(ip_node, asn_node, id=f"e_asn_{hash(val)}", relationship="ROUTED_BY", confidence=0.99)

            elif ioc_type == "SHA256":
                h_node = f"HASH:{val[:12]}..."
                G.add_node(h_node, label=ioc.get("filename", val[:16]), type="ATTACHMENT", threat_status=rep, full_hash=val)
                G.add_edge(case_id, h_node, id=f"e_att_{hash(val)}", relationship="CONTAINS_PAYLOAD", confidence=1.0)

        # 5. Campaign Linkage
        if campaign_info:
            cmp_id = campaign_info.get("id")
            cmp_name = campaign_info.get("name")
            cmp_node = f"CAMPAIGN:{cmp_id}"
            G.add_node(cmp_node, label=f"{cmp_name} ({campaign_info.get('campaign_dna', '')})", type="CAMPAIGN", threat_status="MALICIOUS")
            G.add_edge(case_id, cmp_node, id=f"e_camp_{cmp_id}", relationship="CORRELATED_WITH_CAMPAIGN", confidence=campaign_info.get("confidence", 0.90))

        # Convert NetworkX graph to Cytoscape JSON
        elements = {"nodes": [], "edges": []}
        for node_id, attrs in G.nodes(data=True):
            elements["nodes"].append({
                "data": {
                    "id": str(node_id),
                    "label": attrs.get("label", str(node_id)),
                    "type": attrs.get("type", "UNKNOWN"),
                    "threat_status": attrs.get("threat_status", "UNKNOWN"),
                    **{k: v for k, v in attrs.items() if k not in ("label", "type", "threat_status")}
                }
            })

        for u, v, k, attrs in G.edges(keys=True, data=True):
            edge_id = attrs.get("id") or f"edge_{u}_{v}_{k}"
            elements["edges"].append({
                "data": {
                    "id": edge_id,
                    "source": str(u),
                    "target": str(v),
                    "relationship": attrs.get("relationship", "RELATED_TO"),
                    "confidence": attrs.get("confidence", 0.8),
                    "evidence_id": attrs.get("evidence_id")
                }
            })

        return elements

import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import type { Core } from 'cytoscape';
import type { CytoscapeGraph } from '../types';
import { Network, Info, Maximize2, RefreshCw } from 'lucide-react';

interface Props {
  graphData: CytoscapeGraph;
}

export const EvidenceGraphView: React.FC<Props> = ({ graphData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Convert nodes and edges
    const elements = [
      ...graphData.nodes.map((n) => ({
        group: 'nodes' as const,
        data: n.data,
      })),
      ...graphData.edges.map((e) => ({
        group: 'edges' as const,
        data: e.data,
      })),
    ];

    const styles: any = [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#cbd5e1',
            'font-size': '11px',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'background-color': '#334155',
            'border-width': 2,
            'border-color': '#64748b',
            'width': 34,
            'height': 34,
          },
        },
        {
          selector: 'node[threat_status = "MALICIOUS"]',
          style: {
            'background-color': '#ef4444',
            'border-color': '#f87171',
            'border-width': 3,
          },
        },
        {
          selector: 'node[threat_status = "SUSPICIOUS"]',
          style: {
            'background-color': '#f59e0b',
            'border-color': '#fbbf24',
          },
        },
        {
          selector: 'node[type = "CASE"]',
          style: {
            'background-color': '#0284c7',
            'border-color': '#38bdf8',
            'width': 44,
            'height': 44,
            'shape': 'hexagon',
          },
        },
        {
          selector: 'node[type = "CAMPAIGN"]',
          style: {
            'background-color': '#9333ea',
            'border-color': '#c084fc',
            'width': 44,
            'height': 44,
            'shape': 'diamond',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(relationship)',
            'font-size': '9px',
            'color': '#94a3b8',
            'text-rotation': 'autorotate',
            'text-margin-y': -8,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#38bdf8',
            'border-width': 4,
          },
        },
      ];

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: styles,
      layout: {
        name: 'cose',
        animate: true,
        nodeOverlap: 20,
        componentSpacing: 100,
        nodeRepulsion: () => 450000,
        idealEdgeLength: () => 100,
      },
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      setSelectedNode(node.data());
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData]);

  const fitGraph = () => {
    cyRef.current?.fit(undefined, 30);
  };

  const reLayout = () => {
    cyRef.current?.layout({ name: 'cose', animate: true }).run();
  };

  return (
    <div className="relative border border-slate-800 rounded-xl overflow-hidden bg-slate-950/80 shadow-2xl">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-900/90 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-cyan-400" />
          <span className="text-sm font-semibold text-slate-200">Interactive Forensic Evidence Graph</span>
          <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full border border-slate-700">
            {graphData.nodes.length} Nodes • {graphData.edges.length} Relationships
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fitGraph}
            className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-md border border-slate-700 transition"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            Fit View
          </button>
          <button
            onClick={reLayout}
            className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-md border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Rearrange
          </button>
        </div>
      </div>

      <div className="relative">
        <div ref={containerRef} className="w-full h-[520px] bg-slate-950" />

        {/* Legend */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md p-2.5 rounded-lg border border-slate-800 text-[11px] text-slate-400 flex flex-wrap gap-3 pointer-events-none">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
            <span>Malicious IOC</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
            <span>Suspicious/Mismatch</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block" />
            <span>Campaign Link</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-500 inline-block" />
            <span>Case Anchor</span>
          </div>
        </div>

        {/* Node Inspector Side Panel */}
        {selectedNode && (
          <div className="absolute top-3 right-3 w-80 bg-slate-900/95 backdrop-blur-md border border-slate-700 p-4 rounded-xl shadow-2xl text-xs space-y-3 z-20 animate-in fade-in slide-in-from-right-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Info className="w-4 h-4 text-cyan-400" />
                Node Inspector
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-200"
              >
                ✕
              </button>
            </div>
            <div>
              <span className="text-slate-500 block">Identifier:</span>
              <code className="text-cyan-300 break-all font-mono">{selectedNode.id}</code>
            </div>
            <div>
              <span className="text-slate-500 block">Type:</span>
              <span className="font-semibold text-slate-300">{selectedNode.type}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Threat Status:</span>
              <span
                className={`inline-block px-2 py-0.5 rounded font-bold ${
                  selectedNode.threat_status === 'MALICIOUS'
                    ? 'bg-red-950 text-red-400 border border-red-800'
                    : selectedNode.threat_status === 'SUSPICIOUS'
                    ? 'bg-amber-950 text-amber-400 border border-amber-800'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {selectedNode.threat_status}
              </span>
            </div>
            {selectedNode.full_url && (
              <div>
                <span className="text-slate-500 block">Full URL:</span>
                <code className="text-slate-300 break-all">{selectedNode.full_url}</code>
              </div>
            )}
            {selectedNode.full_hash && (
              <div>
                <span className="text-slate-500 block">Payload SHA-256:</span>
                <code className="text-slate-300 break-all">{selectedNode.full_hash}</code>
              </div>
            )}
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 italic">
              Click background to dismiss inspector.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

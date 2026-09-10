import React, { useEffect, useState } from 'react';
import type { CampaignSummary } from '../types';
import { Dna, Layers, Link as LinkIcon, CheckCircle2 } from 'lucide-react';

interface Props {
  currentCampaignId?: string;
  currentCampaignName?: string;
  currentCampaignDna?: string;
}

export const CampaignView: React.FC<Props> = ({
  currentCampaignId,
  currentCampaignName,
  currentCampaignDna,
}) => {
  const [allCampaigns, setAllCampaigns] = useState<CampaignSummary[]>([]);

  useEffect(() => {
    fetch('/api/v1/campaigns')
      .then((res) => res.json())
      .then((data) => {
        setAllCampaigns(data || []);
      })
      .catch((err) => console.error('Failed to load campaigns:', err));
  }, []);

  // Parse DNA segments
  const dnaParts = (currentCampaignDna || 'H00-D00-U00-I00-A00-L00').split('-');

  return (
    <div className="space-y-6">
      {/* 1. Active Case Campaign DNA Banner */}
      <div className="bg-gradient-to-r from-purple-950/40 via-slate-900 to-slate-900 border border-purple-800/60 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Dna className="w-5 h-5 text-purple-400" />
              <h3 className="text-base font-bold text-slate-100">
                {currentCampaignName ? `Linked Threat Campaign: ${currentCampaignName}` : 'Uncorrelated Incident'}
              </h3>
            </div>
            <p className="text-xs text-slate-400 max-w-xl">
              Campaign DNA is an internal analytical fingerprint encoding multi-dimensional infrastructure
              and header structural attributes to identify observable campaign linkage across cases.
            </p>
          </div>

          <div className="bg-slate-950/90 border border-purple-700/60 px-5 py-3 rounded-xl">
            <span className="text-[10px] text-purple-400 uppercase tracking-widest font-mono block mb-0.5 font-bold">
              Campaign DNA Fingerprint
            </span>
            <span className="text-lg font-black text-slate-100 font-mono tracking-wider">
              {currentCampaignDna || 'H04-D01-U01-I01-A00-L06'}
            </span>
          </div>
        </div>

        {/* DNA Decomposition */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 mt-6 pt-5 border-t border-slate-800/80 text-center">
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Headers</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[0] || 'H00'}</span>
          </div>
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Domains</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[1] || 'D00'}</span>
          </div>
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Payload URLs</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[2] || 'U00'}</span>
          </div>
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Relay IPs</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[3] || 'I00'}</span>
          </div>
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Attachments</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[4] || 'A00'}</span>
          </div>
          <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-500 block">Lexical Length</span>
            <span className="text-sm font-mono font-bold text-cyan-400">{dnaParts[5] || 'L00'}</span>
          </div>
        </div>
      </div>

      {/* 2. Global Campaign Catalog */}
      <div className="space-y-3">
        <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          Active Observed Campaign Clusters ({allCampaigns.length})
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {allCampaigns.map((camp) => {
            const isMatch = camp.id === currentCampaignId;
            return (
              <div
                key={camp.id}
                className={`p-5 rounded-xl border transition ${
                  isMatch
                    ? 'bg-purple-950/20 border-purple-600 shadow-xl shadow-purple-950/30 ring-1 ring-purple-500/50'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="text-xs font-mono text-purple-400 block">{camp.id}</span>
                    <h5 className="font-bold text-slate-100 text-sm">{camp.name}</h5>
                  </div>
                  {isMatch && (
                    <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] font-bold">
                      <CheckCircle2 className="w-3 h-3" />
                      ACTIVE MATCH
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-400 mb-4">{camp.summary}</p>

                <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-800/80">
                  <div className="flex items-center gap-1 font-mono">
                    <Dna className="w-3.5 h-3.5 text-slate-400" />
                    <span>DNA: {camp.campaign_dna}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <LinkIcon className="w-3.5 h-3.5 text-slate-400" />
                    <span>{camp.case_ids.length} Correlated Cases</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

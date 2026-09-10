import React, { useState } from 'react';
import type { ResponseAction } from '../types';
import { CheckCircle, Copy, Check, Terminal, Lock } from 'lucide-react';

interface Props {
  caseId: string;
  actions: ResponseAction[];
}

export const ResponsePlaybookView: React.FC<Props> = ({ caseId, actions }) => {
  const [ruleFormat, setRuleFormat] = useState<string>('suricata');
  const [exportedRules, setExportedRules] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [approvedActionIds, setApprovedActionIds] = useState<Set<string>>(new Set());

  const handleApprove = (id: string) => {
    setApprovedActionIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  const handleFetchRules = async (format: string) => {
    setRuleFormat(format);
    try {
      const res = await fetch(`/api/v1/cases/${caseId}/actions/export-rules?format=${format}`, {
        method: 'POST',
      });
      const data = await res.json();
      setExportedRules(data.rules || '');
    } catch (e) {
      console.error(e);
      setExportedRules('# Failed to export rules');
    }
  };

  const copyRules = () => {
    navigator.clipboard.writeText(exportedRules);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const autoActions = actions.filter((a) => !a.requires_human_approval);
  const approvalActions = actions.filter((a) => a.requires_human_approval);

  return (
    <div className="space-y-6">
      {/* 1. Human Approval Gate Actions */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Lock className="w-4 h-4 text-amber-400" />
            Human Approval Gate Containment Actions ({approvalActions.length})
          </h3>
          <span className="text-[11px] bg-amber-950/60 text-amber-400 px-2 py-0.5 rounded border border-amber-800 font-bold">
            MANDATORY ANALYST GATE
          </span>
        </div>

        <div className="space-y-3">
          {approvalActions.map((act) => {
            const isApproved = approvedActionIds.has(act.id);
            return (
              <div
                key={act.id}
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-950/60 border border-slate-800 transition"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-200">{act.action_type}</span>
                    <code className="text-xs text-cyan-300 font-mono bg-slate-900 px-2 py-0.5 rounded">
                      {act.target}
                    </code>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        act.priority === 'HIGH'
                          ? 'bg-red-950 text-red-400'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {act.priority} PRIORITY
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{act.rationale}</p>
                </div>

                <div className="shrink-0">
                  {isApproved ? (
                    <span className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-950/50 px-3 py-1.5 rounded-lg border border-emerald-800">
                      <CheckCircle className="w-4 h-4" />
                      APPROVED & DISPATCHED
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApprove(act.id)}
                      className="text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 px-4 py-1.5 rounded-lg shadow-lg shadow-amber-500/20 transition"
                    >
                      Authorize & Execute
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Automated Safe Baseline Actions */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            Automated Safe Defense Procedures ({autoActions.length})
          </h3>
          <span className="text-[11px] text-slate-500">Autonomous Execution</span>
        </div>

        <div className="space-y-2">
          {autoActions.map((act) => (
            <div
              key={act.id}
              className="flex items-center justify-between p-3 bg-slate-950/40 rounded-lg border border-slate-800/80 text-xs"
            >
              <div>
                <span className="font-bold text-slate-300 mr-2">{act.action_type}</span>
                <code className="text-slate-400 font-mono">{act.target}</code>
                <p className="text-[11px] text-slate-500 mt-0.5">{act.rationale}</p>
              </div>
              <span className="text-[11px] text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-800/60">
                EXECUTED
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Rule Exporter (Suricata, Snort, Zeek, RPZ DNS, iptables) */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Perimeter Defense Rule Exporter
            </h3>
            <p className="text-xs text-slate-400">
              Compile observed threat IOCs into ready-to-deploy firewall and NIDS rules.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {['suricata', 'snort', 'rpz_dns', 'iptables'].map((fmt) => (
              <button
                key={fmt}
                onClick={() => handleFetchRules(fmt)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition ${
                  ruleFormat === fmt
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {exportedRules ? (
          <div className="relative">
            <pre className="p-4 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-cyan-300 overflow-x-auto max-h-60">
              {exportedRules}
            </pre>
            <button
              onClick={copyRules}
              className="absolute top-3 right-3 flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy Rules'}
            </button>
          </div>
        ) : (
          <div className="p-6 text-center border border-dashed border-slate-800 rounded-xl">
            <button
              onClick={() => handleFetchRules('suricata')}
              className="text-xs font-bold text-cyan-400 hover:underline"
            >
              Click to generate Suricata / Firewall rules from verified IOCs
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

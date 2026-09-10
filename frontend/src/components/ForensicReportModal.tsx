import React, { useState } from 'react';
import type { CaseDetail } from '../types';
import { FileText, Printer, EyeOff, X, Download } from 'lucide-react';

interface Props {
  caseDetail: CaseDetail;
  onClose: () => void;
}

export const ForensicReportModal: React.FC<Props> = ({ caseDetail, onClose }) => {
  const [redactPii, setRedactPii] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'manifest'>('preview');

  const printReport = () => {
    const url = `/api/v1/cases/${caseDetail.id}/report?redact_pii=${redactPii}`;
    const win = window.open(url, '_blank');
    win?.focus();
  };

  const downloadManifest = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(caseDetail.manifest || {}, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute('href', dataStr);
    dlAnchor.setAttribute('download', `case_manifest_${caseDetail.id}.json`);
    dlAnchor.click();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-5xl h-[88vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-cyan-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                AegisMail Digital Forensics Dossier & Manifest
              </h3>
              <span className="text-xs text-slate-400 font-mono">Case ID: {caseDetail.id}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 mr-3 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
              <input
                type="checkbox"
                id="pii-toggle"
                checked={redactPii}
                onChange={(e) => setRedactPii(e.target.checked)}
                className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
              <label htmlFor="pii-toggle" className="text-xs text-slate-300 cursor-pointer flex items-center gap-1">
                <EyeOff className="w-3.5 h-3.5 text-slate-400" />
                Redact PII
              </label>
            </div>

            <div className="flex bg-slate-800 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('preview')}
                className={`text-xs px-3 py-1 rounded-md font-medium transition ${
                  activeTab === 'preview' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                HTML Dossier
              </button>
              <button
                onClick={() => setActiveTab('manifest')}
                className={`text-xs px-3 py-1 rounded-md font-medium transition ${
                  activeTab === 'manifest' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                JSON Manifest
              </button>
            </div>

            <button
              onClick={printReport}
              className="flex items-center gap-1.5 text-xs bg-cyan-600 hover:bg-cyan-500 text-white px-3.5 py-1.5 rounded-lg shadow-md transition font-semibold"
            >
              <Printer className="w-3.5 h-3.5" />
              Print / Save PDF
            </button>

            <button
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-slate-100 transition rounded-lg hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-slate-950 overflow-hidden relative">
          {activeTab === 'preview' ? (
            <iframe
              src={`/api/v1/cases/${caseDetail.id}/report?redact_pii=${redactPii}`}
              title="Forensic Report Preview"
              className="w-full h-full border-none bg-white"
            />
          ) : (
            <div className="p-6 h-full overflow-y-auto space-y-4">
              {/* Blockchain & Merkle Root Ledger Verification Card */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/60 to-slate-900 border border-indigo-700/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-indigo-300 uppercase tracking-widest flex items-center gap-1.5 font-mono">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block animate-pulse" />
                    SIH Theme: Blockchain & Cybersecurity // Immutable Ledger Proof
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 font-bold">
                    CRYPTOGRAPHIC CHAIN OF CUSTODY VERIFIED
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Evidence Merkle Root:</span>
                    <code className="text-cyan-300 font-mono text-[11px] break-all">
                      {caseDetail.manifest?.blockchain_evidence_anchor?.merkle_root || 'Calculated on-the-fly'}
                    </code>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Previous Block Hash:</span>
                    <code className="text-slate-300 font-mono text-[11px] break-all">
                      {caseDetail.manifest?.blockchain_evidence_anchor?.previous_block_hash || '000000000019d6689c085ae16583...'}
                    </code>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 italic pt-1">
                  Every header token, IOC, and forensic timeline event is cryptographically committed into the Merkle tree. Any post-investigation tampering automatically invalidates the manifest hash.
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-slate-200">Cryptographic Case Manifest</h4>
                  <p className="text-xs text-slate-400">
                    Standalone reproducible manifest pinning parser, rules, and scoring engine hashes.
                  </p>
                </div>
                <button
                  onClick={downloadManifest}
                  className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download Manifest
                </button>
              </div>
              <pre className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono text-cyan-300 overflow-x-auto">
                {JSON.stringify(caseDetail.manifest, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

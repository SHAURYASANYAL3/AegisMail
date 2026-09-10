import React, { useState } from 'react';
import type { RelayHop } from '../types';
import { ShieldCheck, ShieldAlert, AlertTriangle, Clock, Server, Terminal } from 'lucide-react';

interface Props {
  spfStatus: string;
  dkimStatus: string;
  dmarcStatus: string;
  relayHops: RelayHop[];
  headersJson?: string;
}

export const HeaderForensicsView: React.FC<Props> = ({
  spfStatus,
  dkimStatus,
  dmarcStatus,
  relayHops,
  headersJson,
}) => {
  const [showRaw, setShowRaw] = useState(false);

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PASS':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 rounded-lg text-xs font-bold">
            <ShieldCheck className="w-3.5 h-3.5" />
            PASS
          </span>
        );
      case 'FAIL':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-red-950/80 text-red-400 border border-red-800/80 rounded-lg text-xs font-bold">
            <ShieldAlert className="w-3.5 h-3.5" />
            FAIL
          </span>
        );
      case 'SOFTFAIL':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-amber-950/80 text-amber-400 border border-amber-800/80 rounded-lg text-xs font-bold">
            <AlertTriangle className="w-3.5 h-3.5" />
            SOFTFAIL
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-800 text-slate-400 border border-slate-700 rounded-lg text-xs font-bold">
            NONE / UNKNOWN
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Cryptographic Authentication Matrix */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            Deterministic Email Authentication
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">
            RFC 7208 (SPF) • RFC 6376 (DKIM) • RFC 7489 (DMARC)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">SPF Verification</span>
              {getStatusBadge(spfStatus)}
            </div>
            <p className="text-xs text-slate-400">
              Validates that the originating relay mail server is explicitly authorized in the sender domain DNS SPF TXT record.
            </p>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">DKIM Cryptographic Signature</span>
              {getStatusBadge(dkimStatus)}
            </div>
            <p className="text-xs text-slate-400">
              Validates public key cryptography signature integrity over message body and invariant headers in transit.
            </p>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-300">DMARC Domain Alignment</span>
              {getStatusBadge(dmarcStatus)}
            </div>
            <p className="text-xs text-slate-400">
              Enforces sender policy alignment between RFC 5322 From domain and verified SPF/DKIM identifier domains.
            </p>
          </div>
        </div>
      </div>

      {/* 2. Chronological Relay Hop Latency Chain */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            Reconstructed Mail Relay Path (Chronological)
          </h3>
          <span className="text-xs text-slate-400">{relayHops.length} Observed Network Hops</span>
        </div>

        {relayHops.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">No Received headers found in artifact.</p>
        ) : (
          <div className="space-y-3 relative before:absolute before:left-6 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-800">
            {relayHops.map((hop, idx) => (
              <div
                key={idx}
                className={`relative flex items-start gap-4 p-3.5 rounded-lg border transition ${
                  hop.is_suspicious
                    ? 'bg-red-950/20 border-red-800/60'
                    : 'bg-slate-950/40 border-slate-800/80'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold z-10 ${
                    hop.is_suspicious
                      ? 'bg-red-500 text-white shadow-lg shadow-red-500/50'
                      : 'bg-slate-800 text-slate-300 border border-slate-700'
                  }`}
                >
                  {hop.hop_index}
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <span className="font-semibold text-slate-200 text-xs">
                      From: <code className="text-cyan-300 font-mono">{hop.from_host || 'unknown'}</code>
                      {hop.sender_ip && (
                        <span className="ml-2 px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[11px] font-mono">
                          [{hop.sender_ip}]
                        </span>
                      )}
                    </span>
                    {hop.delay_seconds !== null && hop.delay_seconds !== undefined && (
                      <span className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
                        <Clock className="w-3 h-3 text-slate-500" />
                        Hop transit: {hop.delay_seconds}s
                      </span>
                    )}
                  </div>

                  <div className="text-xs text-slate-400">
                    Handled by <code className="text-slate-300">{hop.by_host}</code> via{' '}
                    <span className="text-slate-300 font-semibold">{hop.protocol}</span>
                  </div>

                  {hop.timestamp && (
                    <div className="text-[11px] text-slate-500 font-mono">{hop.timestamp}</div>
                  )}

                  {hop.is_suspicious && (
                    <div className="mt-1 flex items-center gap-1 text-[11px] text-red-400 font-semibold">
                      <AlertTriangle className="w-3 h-3" />
                      Anomalous or known hostile relay IP address detected.
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Raw Headers Toggle */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="flex items-center gap-2 text-xs font-bold text-slate-300 hover:text-cyan-400 transition"
        >
          <Terminal className="w-4 h-4" />
          {showRaw ? 'Hide Raw MIME Headers' : 'Inspect Raw MIME Headers'}
        </button>
        {showRaw && headersJson && (
          <pre className="mt-3 p-4 bg-slate-950 border border-slate-800 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto max-h-80">
            {JSON.stringify(JSON.parse(headersJson), null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

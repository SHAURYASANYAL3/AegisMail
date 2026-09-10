import React, { useState } from 'react';
import type { IOC } from '../types';
import { Search, Copy, Check, Globe, AlertCircle } from 'lucide-react';

interface Props {
  iocs: IOC[];
}

export const IOCTable: React.FC<Props> = ({ iocs }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const filteredIocs = iocs.filter((ioc) => {
    const matchesSearch =
      ioc.value.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (ioc.asn_org && ioc.asn_org.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (ioc.country && ioc.country.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesType = filterType === 'ALL' || ioc.ioc_type === filterType;
    return matchesSearch && matchesType;
  });

  const getRepBadge = (rep: string) => {
    switch (rep) {
      case 'MALICIOUS':
        return <span className="px-2 py-0.5 rounded bg-red-950/80 text-red-400 border border-red-800 text-[10px] font-bold">MALICIOUS</span>;
      case 'SUSPICIOUS':
        return <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800 text-[10px] font-bold">SUSPICIOUS</span>;
      case 'BENIGN':
        return <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800 text-[10px] font-bold">BENIGN</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 text-[10px] font-bold">UNKNOWN</span>;
    }
  };

  return (
    <div className="space-y-4">
      {/* Attribution Boundary Banner */}
      <div className="flex items-start gap-3 p-3.5 bg-amber-950/30 border border-amber-800/60 rounded-xl text-xs text-amber-300">
        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Attribution Boundary Notice:</span> Geolocation and ASN metrics identify observed
          hosting and relay infrastructure, not the physical sovereign identity of the attacker. Confidence metrics reflect
          evidentiary density.
        </div>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/60 p-3.5 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search indicator, ASN, country..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {['ALL', 'IPV4', 'DOMAIN', 'URL', 'SHA256', 'EMAIL'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`text-xs px-2.5 py-1 rounded-md transition font-medium ${
                filterType === t
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-800/60'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Indicator Value</th>
                <th className="px-4 py-3">Reputation</th>
                <th className="px-4 py-3">Observed ASN / Org</th>
                <th className="px-4 py-3">Observed Geolocation</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredIocs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No indicators found matching the criteria.
                  </td>
                </tr>
              ) : (
                filteredIocs.map((ioc, idx) => (
                  <tr key={ioc.id || idx} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-3 font-mono font-bold text-slate-400">
                      <span className="px-1.5 py-0.5 bg-slate-800 rounded text-[10px] text-slate-300">
                        {ioc.ioc_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-200 break-all max-w-xs">
                      {ioc.value}
                    </td>
                    <td className="px-4 py-3">{getRepBadge(ioc.reputation)}</td>
                    <td className="px-4 py-3 text-slate-300">
                      {ioc.asn_org ? (
                        <span>
                          <span className="font-mono text-cyan-400">{ioc.asn}</span> {ioc.asn_org}
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">Not applicable</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-300">
                      {ioc.country ? (
                        <div className="flex items-center gap-1.5">
                          <Globe className="w-3.5 h-3.5 text-slate-400" />
                          <span>
                            {ioc.city ? `${ioc.city}, ` : ''}
                            {ioc.country}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            ({intToPercent(ioc.confidence)}%)
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">Unresolved</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleCopy(ioc.id || String(idx), ioc.value)}
                        className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition"
                        title="Copy IOC"
                      >
                        {copiedId === (ioc.id || String(idx)) ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

function intToPercent(num?: number): number {
  if (!num) return 50;
  return Math.round(num * 100);
}

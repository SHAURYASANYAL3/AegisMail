import React, { useState, useEffect } from 'react';
import type { CaseDetail } from './types';
import { EvidenceGraphView } from './components/EvidenceGraphView';
import { HeaderForensicsView } from './components/HeaderForensicsView';
import { IOCTable } from './components/IOCTable';
import { CounterfactualView } from './components/CounterfactualView';
import { CampaignView } from './components/CampaignView';
import { ResponsePlaybookView } from './components/ResponsePlaybookView';
import { ForensicReportModal } from './components/ForensicReportModal';
import { GeoLocationMapView } from './components/GeoLocationMapView';
import {
  ShieldAlert,
  UploadCloud,
  FileText,
  Network,
  Sliders,
  Dna,
  Zap,
  Activity,
  Copy,
  Check,
  Terminal,
  Globe,
  WifiOff,
  Sparkles,
  MapPin
} from 'lucide-react';

export const App: React.FC = () => {
  const queryParams = new URLSearchParams(window.location.search);
  const initialTab = queryParams.get('tab') || 'overview';
  const initialDemo = queryParams.get('demo') || 'demo_case_01_phish_creds';
  const initialReport = queryParams.get('report') === 'true';

  const [currentCase, setCurrentCase] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string>(initialTab);
  const [showReportModal, setShowReportModal] = useState(initialReport);
  const [copiedHash, setCopiedHash] = useState(false);

  // Auto-load demo on initial load
  useEffect(() => {
    loadDemoCase(initialDemo);
  }, [initialDemo]);

  const loadDemoCase = async (demoName: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/cases/analyze-demo/${demoName}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to load demo case');
      const data: CaseDetail = await res.json();
      setCurrentCase(data);
      setActiveTab('overview');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/cases/upload', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to upload email artifact');
      const data: CaseDetail = await res.json();
      setCurrentCase(data);
      setActiveTab('overview');
    } catch (err) {
      console.error(err);
      alert('Error analyzing uploaded EML artifact.');
    } finally {
      setLoading(false);
    }
  };

  const copyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const getThreatBadge = (threatClass: string) => {
    switch (threatClass) {
      case 'BENIGN':
        return 'bg-emerald-950/80 text-emerald-400 border-emerald-800';
      case 'INSUFFICIENT_EVIDENCE':
      case 'UNKNOWN / NEEDS_REVIEW':
        return 'bg-amber-950/80 text-amber-400 border-amber-800';
      default:
        return 'bg-red-950/80 text-red-400 border-red-800';
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight text-white">
                AEGIS<span className="text-cyan-400">MAIL</span>
              </span>
              <span className="text-[10px] bg-cyan-950 text-cyan-300 font-mono px-2 py-0.5 rounded border border-cyan-800 font-semibold">
                SIH26106 DFIR PLATFORM
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Evidence-Correlated AI Email Forensics & Threat Intelligence
            </p>
          </div>
        </div>

        {/* Action Controls & Demo Switcher */}
        <div className="flex items-center gap-3">
          {/* Offline Pill */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 bg-emerald-950/40 text-emerald-400 border border-emerald-800/50 rounded-lg text-xs font-semibold">
            <WifiOff className="w-3.5 h-3.5" />
            <span>100% Offline / $0 API Key</span>
          </div>

          {/* Quick Demo Case Selector */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1 text-xs">
            <span className="text-slate-400 font-medium text-[11px]">Demo:</span>
            <select
              onChange={(e) => loadDemoCase(e.target.value)}
              defaultValue="demo_case_01_phish_creds"
              className="bg-transparent text-cyan-300 font-semibold focus:outline-none cursor-pointer text-xs"
            >
              <option value="demo_case_01_phish_creds" className="bg-slate-900 text-slate-200">
                1. M365 Credential Phish (SPF Fail)
              </option>
              <option value="demo_case_02_bec_wire" className="bg-slate-900 text-slate-200">
                2. Executive Wire BEC (Reply-To Spoof)
              </option>
              <option value="demo_case_03_campaign_part1" className="bg-slate-900 text-slate-200">
                3. Campaign Alpha (AgentTesla Payload)
              </option>
              <option value="demo_case_04_campaign_part2" className="bg-slate-900 text-slate-200">
                4. Campaign Beta (Linked C2 Infra)
              </option>
              <option value="demo_case_05_adversarial_test" className="bg-slate-900 text-slate-200">
                5. Hostile Prompt Injection Attempt
              </option>
              <option value="demo_case_06_legitimate_newsletter" className="bg-slate-900 text-slate-200">
                6. Benign Aligned Newsletter (SPF/DKIM Pass)
              </option>
              <option value="demo_case_07_ambiguous_marketing" className="bg-slate-900 text-slate-200">
                7. Ambiguous (Insufficient Evidence)
              </option>
            </select>
          </div>

          {/* Upload EML */}
          <label className="flex items-center gap-1.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 cursor-pointer transition">
            <UploadCloud className="w-4 h-4 text-cyan-400" />
            <span>Upload .EML</span>
            <input
              type="file"
              accept=".eml,.msg"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>

          {/* Report Button */}
          {currentCase && (
            <button
              onClick={() => setShowReportModal(true)}
              className="flex items-center gap-1.5 text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white px-3.5 py-1.5 rounded-lg shadow-lg shadow-cyan-600/20 transition"
            >
              <FileText className="w-4 h-4" />
              <span>Forensic Dossier</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Investigation Workspace */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {loading ? (
          <div className="py-32 flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
            <p className="text-sm font-semibold text-slate-300">
              Preserving cryptographic hashes & executing forensic pipeline...
            </p>
          </div>
        ) : !currentCase ? (
          <div className="py-24 text-center">
            <p className="text-slate-400">Select a demo case or upload an EML artifact to begin investigation.</p>
          </div>
        ) : (
          <>
            {/* Case Header Hero */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-md relative overflow-hidden">
              <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="font-mono text-xs font-black text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-md border border-cyan-800/80">
                      {currentCase.id}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      File: {currentCase.original_filename}
                    </span>
                    <span
                      className={`text-xs font-extrabold uppercase px-3 py-1 rounded-md border tracking-wider ${getThreatBadge(
                        currentCase.threat_class
                      )}`}
                    >
                      {currentCase.threat_class.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <h1 className="text-xl font-black text-slate-100 tracking-tight">
                    {currentCase.subject || 'No Subject Defined'}
                  </h1>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                    <div>
                      <span className="text-slate-500">Sender: </span>
                      <code className="text-slate-300 font-mono">{currentCase.sender || 'unknown'}</code>
                    </div>
                    {currentCase.reply_to && currentCase.reply_to !== currentCase.sender && (
                      <div className="text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/60 font-semibold">
                        <span>Reply-To Deception: </span>
                        <code className="font-mono">{currentCase.reply_to}</code>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono pt-1">
                    <span>SHA-256: {currentCase.sha256_hash}</span>
                    <button
                      onClick={() => copyHash(currentCase.sha256_hash)}
                      className="text-slate-400 hover:text-slate-200"
                      title="Copy SHA-256"
                    >
                      {copiedHash ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Score & Tri-Confidence Gauges */}
                <div className="flex items-center gap-4 bg-slate-950/80 p-4 rounded-xl border border-slate-800/90 shrink-0">
                  {/* Primary Threat Score */}
                  <div className="text-center px-3 border-r border-slate-800">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-0.5">
                      Threat Risk
                    </span>
                    <span
                      className={`text-3xl font-black font-mono ${
                        currentCase.threat_score >= 70
                          ? 'text-red-500'
                          : currentCase.threat_score >= 30
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {currentCase.threat_score}
                      <span className="text-xs text-slate-500 font-normal">/100</span>
                    </span>
                  </div>

                  {/* Tri-Confidence Gauges */}
                  <div className="space-y-1.5 text-xs font-mono">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-slate-400">Threat Conf:</span>
                      <span className="text-cyan-400 font-bold">
                        {Math.round(currentCase.threat_confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-slate-400">Evidence Conf:</span>
                      <span className="text-emerald-400 font-bold">
                        {Math.round(currentCase.evidence_confidence * 100)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-slate-400">Infra Conf:</span>
                      <span className="text-amber-400 font-bold">
                        {Math.round(currentCase.infrastructure_confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Golden Path Workspace Tabs */}
            <div className="flex items-center gap-1.5 border-b border-slate-800 pb-2 overflow-x-auto text-xs font-medium">
              {[
                { id: 'overview', label: 'Executive & AI Overview', icon: Sparkles },
                { id: 'graph', label: 'Evidence Graph', icon: Network },
                { id: 'geomap', label: 'GeoLocation Map', icon: MapPin },
                { id: 'forensics', label: 'Header Forensics & Hops', icon: Activity },
                { id: 'iocs', label: `Observed IOCs (${currentCase.iocs.length})`, icon: Globe },
                { id: 'campaign', label: 'Campaign DNA', icon: Dna },
                { id: 'counterfactual', label: 'Counterfactual Simulator', icon: Sliders },
                { id: 'playbook', label: 'Response Playbook', icon: Zap },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-lg transition font-semibold ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Active Tab View */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Cols: AI Grounded Narrative & Evidentiary Drivers */}
                <div className="lg:col-span-2 space-y-6">
                  {/* AI Grounded Narrative Box */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-cyan-400" />
                        Grounded AI Forensics Narrative
                      </h3>
                      <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800 font-bold">
                        ZERO HALLUCINATIONS GUARANTEE
                      </span>
                    </div>
                    <div className="text-xs text-slate-300 whitespace-pre-line leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-slate-800 font-mono">
                      {currentCase.ai_summary || 'No narrative synthesized.'}
                    </div>
                  </div>

                  {/* Evidentiary Risk Contributions */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-3">
                    <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-cyan-400" />
                      Traceable Evidence Contributions ({currentCase.evidence_items.length})
                    </h3>
                    <div className="space-y-2">
                      {currentCase.evidence_items.length === 0 ? (
                        <p className="text-xs text-slate-500">No active risk evidence items registered.</p>
                      ) : (
                        currentCase.evidence_items.map((ev) => (
                          <div
                            key={ev.id}
                            className="flex items-start justify-between gap-4 p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs"
                          >
                            <div className="space-y-0.5">
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-slate-200">{ev.title}</span>
                                <code className="text-[10px] text-slate-400 font-mono bg-slate-800 px-1.5 py-0.5 rounded">
                                  {ev.id}
                                </code>
                              </div>
                              <p className="text-slate-400">{ev.description}</p>
                            </div>
                            <span
                              className={`font-mono font-bold text-xs shrink-0 px-2 py-0.5 rounded ${
                                ev.risk_contribution > 0
                                  ? 'bg-red-950/80 text-red-400 border border-red-800'
                                  : 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                              }`}
                            >
                              {ev.risk_contribution > 0 ? `+${ev.risk_contribution} pts` : 'ALIGNED'}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Right 1 Col: Raw Body Preview & Chain of Custody Events */}
                <div className="space-y-6">
                  {/* Email Body Preview */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-3">
                    <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <FileText className="w-4 h-4 text-cyan-400" />
                      Sanitized Email Body
                    </h3>
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg max-h-64 overflow-y-auto text-xs text-slate-300 font-mono whitespace-pre-wrap">
                      {currentCase.body_text_sanitized ||
                        (currentCase.body_html_sanitized ? (
                          <div dangerouslySetInnerHTML={{ __html: currentCase.body_html_sanitized }} />
                        ) : (
                          'No body content available'
                        ))}
                    </div>
                  </div>

                  {/* Investigation Timeline */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-3">
                    <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-cyan-400" />
                      Chain-of-Custody Timeline ({currentCase.timeline.length})
                    </h3>
                    <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                      {currentCase.timeline.map((evt) => (
                        <div key={evt.id} className="text-xs space-y-0.5 border-l-2 border-slate-700 pl-3">
                          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                            <span>{evt.actor}</span>
                            <span>{evt.event_type}</span>
                          </div>
                          <p className="text-slate-300 text-[11px]">{evt.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'graph' && <EvidenceGraphView graphData={currentCase.graph} />}

            {activeTab === 'geomap' && <GeoLocationMapView iocs={currentCase.iocs} />}

            {activeTab === 'forensics' && (
              <HeaderForensicsView
                spfStatus={currentCase.spf_status}
                dkimStatus={currentCase.dkim_status}
                dmarcStatus={currentCase.dmarc_status}
                relayHops={currentCase.relay_hops}
                headersJson={JSON.stringify(currentCase.raw_headers_json || '{}')}
              />
            )}

            {activeTab === 'iocs' && <IOCTable iocs={currentCase.iocs} />}

            {activeTab === 'campaign' && (
              <CampaignView
                currentCampaignId={currentCase.campaign_id}
                currentCampaignName={currentCase.campaign_name}
                currentCampaignDna={currentCase.campaign_dna}
              />
            )}

            {activeTab === 'counterfactual' && (
              <CounterfactualView
                initialScore={currentCase.threat_score}
                counterfactuals={currentCase.counterfactuals}
              />
            )}

            {activeTab === 'playbook' && (
              <ResponsePlaybookView caseId={currentCase.id} actions={currentCase.recommended_actions} />
            )}
          </>
        )}
      </main>

      {/* Forensic Report Modal */}
      {showReportModal && currentCase && (
        <ForensicReportModal caseDetail={currentCase} onClose={() => setShowReportModal(false)} />
      )}
    </div>
  );
};

export default App;

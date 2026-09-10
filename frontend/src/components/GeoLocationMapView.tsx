import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import type { IOC } from '../types';
import { Globe, AlertCircle } from 'lucide-react';

interface Props {
  iocs: IOC[];
}

export const GeoLocationMapView: React.FC<Props> = ({ iocs }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Filter IOCs with valid coordinates
  const geoIocs = iocs.filter((i) => i.latitude !== undefined && i.latitude !== null && i.longitude !== undefined && i.longitude !== null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Fix default Leaflet icon paths
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    });

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [30.0, 10.0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 12,
      });

      // Dark theme tiles (CartoDB Dark Matter with OSM fallback)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing markers
    map.eachLayer((layer) => {
      if (layer instanceof L.CircleMarker || layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    const bounds = L.latLngBounds([]);

    geoIocs.forEach((ioc) => {
      if (ioc.latitude === undefined || ioc.longitude === undefined) return;

      const isMalicious = ioc.reputation === 'MALICIOUS';
      const isSuspicious = ioc.reputation === 'SUSPICIOUS';
      const color = isMalicious ? '#ef4444' : isSuspicious ? '#f59e0b' : '#10b981';

      const circleMarker = L.circleMarker([ioc.latitude, ioc.longitude], {
        radius: 8,
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85,
      }).addTo(map);

      bounds.extend([ioc.latitude, ioc.longitude]);

      const popupHtml = `
        <div style="font-family: system-ui, sans-serif; font-size: 11px; line-height: 1.4; color: #0f172a; min-width: 180px;">
          <div style="font-weight: 800; font-size: 12px; margin-bottom: 4px; color: ${color};">
            ${ioc.reputation} INFRASTRUCTURE
          </div>
          <div style="font-family: monospace; font-weight: bold; margin-bottom: 4px;">${ioc.value}</div>
          <div><strong>ASN:</strong> ${ioc.asn || 'N/A'} (${ioc.asn_org || 'Unknown'})</div>
          <div><strong>Observed Location:</strong> ${ioc.city ? ioc.city + ', ' : ''}${ioc.country || 'Unknown'}</div>
          <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid #e2e8f0;">
            <strong>Confidence:</strong> ${Math.round(ioc.confidence * 100)}%
          </div>
          <div style="font-size: 9px; color: #64748b; margin-top: 4px; font-style: italic;">
            Identifies observed relay infrastructure, not physical attacker identity.
          </div>
        </div>
      `;

      circleMarker.bindPopup(popupHtml);
    });

    if (geoIocs.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 6 });
    }

    return () => {
      // Keep map instance across renders or resize
    };
  }, [geoIocs]);

  return (
    <div className="space-y-6">
      {/* Attribution Boundary Banner */}
      <div className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-4 text-xs text-amber-300 flex items-start gap-3 shadow-lg">
        <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-bold text-slate-100 uppercase tracking-wider text-[11px] block">
            Observed Infrastructure Forensics vs Physical Attribution
          </span>
          <p className="text-amber-200/90 leading-relaxed">
            Geolocation pinpoints the physical hosting facility of the <strong>observed mail relay, nameserver, or C2 proxy</strong>.
            Cyber adversaries frequently utilize offshore bulletproof VPS providers, compromised webmail relays, and VPN nodes.
            AegisMail never equates server geolocation with the physical location or sovereign identity of the human perpetrator.
          </p>
        </div>
      </div>

      {/* Map Card */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950 shadow-2xl relative">
        <div className="flex items-center justify-between px-5 py-3.5 bg-slate-900/90 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Observed Infrastructure Geolocation Map
            </span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
              {geoIocs.length} Mapped Nodes
            </span>
          </div>

          <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
              Malicious Host
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
              Suspicious Relay
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
              Legitimate Transit
            </span>
          </div>
        </div>

        {/* Leaflet container */}
        <div ref={mapContainerRef} className="w-full h-[480px] bg-slate-950" />
      </div>

      {/* Geolocation Telemetry Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {geoIocs.map((ioc, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2 text-xs"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-cyan-400 font-bold">{ioc.value}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  ioc.reputation === 'MALICIOUS'
                    ? 'bg-red-950 text-red-400 border border-red-800'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {ioc.reputation}
              </span>
            </div>
            <div className="text-slate-300">
              <strong>Location:</strong> {ioc.city ? `${ioc.city}, ` : ''}{ioc.country}
            </div>
            <div className="text-slate-400">
              <strong>Routing Org:</strong> {ioc.asn_org} (<span className="font-mono text-slate-300">{ioc.asn}</span>)
            </div>
            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
              <span className="text-slate-500">Confidence Metric:</span>
              <span className="font-mono text-emerald-400 font-bold">
                {Math.round(ioc.confidence * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

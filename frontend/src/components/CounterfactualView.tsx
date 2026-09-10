import React, { useState } from 'react';
import type { Counterfactual } from '../types';
import { Sliders, TrendingDown, ArrowRight, RotateCcw } from 'lucide-react';

interface Props {
  initialScore: number;
  counterfactuals: Counterfactual[];
}

export const CounterfactualView: React.FC<Props> = ({ initialScore, counterfactuals }) => {
  const [toggled, setToggled] = useState<Record<number, boolean>>({});

  const toggleFeature = (index: number) => {
    setToggled((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const resetAll = () => {
    setToggled({});
  };

  // Calculate simulated score
  let deltaTotal = 0;
  counterfactuals.forEach((c, idx) => {
    if (toggled[idx]) {
      deltaTotal += c.delta_score;
    }
  });

  const simulatedScore = Math.max(0, Math.min(100, initialScore + deltaTotal));

  return (
    <div className="space-y-6">
      {/* Simulation Header / Score Meter */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sliders className="w-5 h-5 text-cyan-400" />
              <h3 className="text-base font-bold text-slate-100">
                Interactive Counterfactual Risk Simulator
              </h3>
            </div>
            <p className="text-xs text-slate-400 max-w-xl">
              Simulate hypothetical state changes to understand which forensic signals drive the verdict.
              Toggle conditions below to see real-time impact on the aggregated threat score.
            </p>
          </div>

          <div className="flex items-center gap-6 bg-slate-950/80 px-6 py-3 rounded-xl border border-slate-800">
            <div className="text-center">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                Baseline
              </span>
              <span className="text-2xl font-black text-red-500 font-mono">{initialScore}</span>
            </div>

            <ArrowRight className="w-5 h-5 text-slate-600" />

            <div className="text-center">
              <span className="text-[10px] text-cyan-400 uppercase tracking-wider block font-semibold">
                Simulated
              </span>
              <span className="text-2xl font-black text-cyan-400 font-mono">{simulatedScore}</span>
            </div>

            {deltaTotal !== 0 && (
              <div className="flex items-center gap-1 text-emerald-400 text-xs font-bold font-mono">
                <TrendingDown className="w-4 h-4" />
                {deltaTotal} pts
              </div>
            )}
          </div>
        </div>

        {Object.keys(toggled).length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-800 flex justify-end">
            <button
              onClick={resetAll}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition"
            >
              <RotateCcw className="w-3 h-3" />
              Reset All Simulations
            </button>
          </div>
        )}
      </div>

      {/* Toggable Features List */}
      <div className="space-y-3">
        {counterfactuals.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800 p-8 rounded-xl text-center text-slate-500 text-xs">
            No active risk drivers detected for counterfactual simulation (Case is benign or insufficient evidence).
          </div>
        ) : (
          counterfactuals.map((item, idx) => {
            const isSimulated = !!toggled[idx];
            return (
              <div
                key={idx}
                onClick={() => toggleFeature(idx)}
                className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition select-none ${
                  isSimulated
                    ? 'bg-cyan-950/20 border-cyan-800/80 shadow-lg shadow-cyan-950/30'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-200">{item.feature_name}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800 text-[10px] font-mono font-bold">
                      {item.delta_score} pts if resolved
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{item.explanation}</p>
                </div>

                <div className="shrink-0 flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block uppercase font-mono">Simulate</span>
                    <span className={`text-xs font-bold ${isSimulated ? 'text-cyan-400' : 'text-slate-400'}`}>
                      {isSimulated ? 'APPLIED' : 'BASELINE'}
                    </span>
                  </div>
                  <div
                    className={`w-11 h-6 rounded-full transition relative flex items-center px-1 ${
                      isSimulated ? 'bg-cyan-600' : 'bg-slate-800'
                    }`}
                  >
                    <div
                      className={`w-4 h-4 rounded-full bg-white transition transform ${
                        isSimulated ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

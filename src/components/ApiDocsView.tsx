import React, { useState } from 'react';
import { Terminal, Send, Copy, Check, Code2, Server, Globe, Key, Shield } from 'lucide-react';
import { LanguageCode } from '../types';

interface ApiDocsViewProps {
  lang: LanguageCode;
  darkMode: boolean;
}

export const ApiDocsView: React.FC<ApiDocsViewProps> = ({
  lang,
  darkMode,
}) => {
  const [activeEndpoint, setActiveEndpoint] = useState<string>('post_sim_run');
  const [responseOutput, setResponseOutput] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const endpoints = [
    {
      id: 'post_sim_run',
      method: 'POST',
      path: '/api/v1/simulations/run',
      title: 'Run Calibrated Digital Twin Simulation',
      desc: 'Executes hybrid metapopulation SEIR + ABM model across Kenya 47 counties with custom NPI parameters.',
      requestBody: {
        name: "Custom Evaluation Run",
        pathogen: "covid19",
        duration_days: 90,
        r0_baseline: 2.4,
        random_seed: 42,
        is_synthetic: false,
        interventions: {
          school_closure: { active: true, start_day: 14, duration_days: 30, compliance_rate: 0.85 },
          vaccination: { active: true, strategy: "occupation_prioritized", daily_doses_per_10k: 35, start_day: 10 },
          household_distancing: { active: true, adaptation_for_informal_settlements: true, start_day: 14, duration_days: 45 },
          mobility_restriction: { active: false, inter_county_reduction: 0.5 },
          face_masks: { active: true, coverage: 0.70 }
        }
      }
    },
    {
      id: 'get_validation',
      method: 'GET',
      path: '/api/v1/validation/status',
      title: 'Get Scientific Validation Status & Criteria',
      desc: 'Returns H1 evaluation criteria, external validation status (2023-2024), and dataset coverage audit.',
      requestBody: null
    },
    {
      id: 'get_counties',
      method: 'GET',
      path: '/api/v1/counties',
      title: 'Get 47 Subcounty Geodata & KNBS/KDHS Indicators',
      desc: 'Retrieves 2019 Census population, KMFL ICU beds (null where unverified), KDHS poverty quintiles.',
      requestBody: null
    },
    {
      id: 'post_ai_chat',
      method: 'POST',
      path: '/api/v1/ai/chat',
      title: 'Ask AI Epidemiologist Copilot',
      desc: 'Invokes local Ollama model (qwen2.5:0.5b) with structured simulation state and public health domain expertise.',
      requestBody: {
        message: "What is the projected ICU peak demand under standard vaccination?",
        simulation_context: { pathogen: "covid19", r0_baseline: 2.4 }
      }
    },
    {
      id: 'get_health',
      method: 'GET',
      path: '/api/v1/health',
      title: 'FastAPI Production Health & Telemetry',
      desc: 'Checks FastAPI backend status, PostGIS connection, and system telemetry.',
      requestBody: null
    }
  ];

  const current = endpoints.find(e => e.id === activeEndpoint) || endpoints[0];

  const handleExecuteRequest = async () => {
    setIsLoading(true);
    setResponseOutput(null);

    try {
      const options: RequestInit = {
        method: current.method,
        headers: { 'Content-Type': 'application/json' },
      };

      if (current.requestBody && current.method === 'POST') {
        options.body = JSON.stringify(current.requestBody);
      }

      const res = await fetch(current.path, options);
      const data = await res.json();
      setResponseOutput(JSON.stringify(data, null, 2));
    } catch (err: any) {
      setResponseOutput(JSON.stringify({ error: err.message, status: 'client_call_fallback' }, null, 2));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!responseOutput) return;
    navigator.clipboard.writeText(responseOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div id="api_docs_view" className="space-y-6 w-full">
      {/* Header */}
      <div className={`p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl flex flex-col md:flex-row items-center justify-between gap-4`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Code2 size={20} className="text-blue-400" />
            <h3 className={`text-sm font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>OpenAPI 3.0 REST Interface & Swagger Sandbox</h3>
          </div>
          <p className={`text-xs ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
            Programmatic API access for epidemiological researchers, DHIS2 integration, and automated pipeline execution
          </p>
        </div>

        <div className={`flex items-center gap-3 text-xs font-mono px-3 py-1.5 rounded-xl ${darkMode ? 'bg-slate-950 border border-slate-800 text-slate-300' : 'bg-slate-100 border border-slate-200 text-slate-600'}`}>
          <Server size={14} className="text-emerald-400" />
          <span>Base URL: <strong className="text-blue-400">/api</strong></span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Endpoint List */}
        <div className={`p-4 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-2`}>
          <span className={`text-xs font-bold uppercase tracking-wider block px-2 mb-2 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Available Endpoints</span>

          {endpoints.map((ep) => (
            <button
              key={ep.id}
              onClick={() => {
                setActiveEndpoint(ep.id);
                setResponseOutput(null);
              }}
              className={`w-full text-left p-3 rounded-xl border transition flex flex-col gap-1 ${
                activeEndpoint === ep.id
                  ? 'bg-blue-600/20 border-blue-500 ring-2 ring-blue-500/20'
                  : darkMode ? 'bg-slate-950/60 border-slate-800 hover:border-slate-700' : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                  ep.method === 'POST' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                }`}>
                  {ep.method}
                </span>
                <span className={`text-xs font-mono font-semibold truncate ${darkMode ? 'text-slate-200' : 'text-slate-800'}`}>{ep.path}</span>
              </div>
              <span className={`text-[11px] line-clamp-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{ep.title}</span>
            </button>
          ))}
        </div>

        {/* Right 2 cols: Interactive Sandbox */}
        <div className={`lg:col-span-2 p-5 rounded-2xl border ${darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200'} shadow-xl space-y-4`}>
          <div className={`flex items-center justify-between pb-3 border-b ${darkMode ? 'border-slate-800' : 'border-slate-200'}`}>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-mono font-bold px-2 py-1 rounded ${
                current.method === 'POST' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              }`}>
                {current.method}
              </span>
              <span className={`text-sm font-mono font-bold ${darkMode ? 'text-slate-100' : 'text-slate-900'}`}>{current.path}</span>
            </div>

            <button
              id="btn_send_api_request"
              onClick={handleExecuteRequest}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition cursor-pointer"
            >
              <Send size={14} />
              {isLoading ? 'Executing...' : 'Try It Out (Send)'}
            </button>
          </div>

          <p className={`text-xs leading-relaxed ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>{current.desc}</p>

          {/* Request Payload (if POST) */}
          {current.requestBody && (
            <div>
              <span className={`text-[11px] font-mono uppercase tracking-wider block mb-1 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Request Payload (JSON):</span>
              <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-emerald-400 overflow-x-auto max-h-48">
                {JSON.stringify(current.requestBody, null, 2)}
              </pre>
            </div>
          )}

          {/* Response Box */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className={`text-[11px] font-mono uppercase tracking-wider ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>Live Response Payload:</span>
              {responseOutput && (
                <button
                  onClick={handleCopy}
                  className={`flex items-center gap-1 text-[11px] transition ${darkMode ? 'text-slate-400 hover:text-white' : 'text-slate-500 hover:text-slate-900'}`}
                >
                  {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy JSON'}
                </button>
              )}
            </div>

            <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-blue-300 overflow-x-auto min-h-48 max-h-80">
              {responseOutput || '// Click "Try It Out (Send)" above to trigger live API response.'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

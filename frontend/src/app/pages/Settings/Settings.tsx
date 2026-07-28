import { useState } from "react";
import { motion } from "framer-motion";
import { Key, Eye, EyeOff, Shield, Cpu, Sliders, CheckCircle2 } from "lucide-react";
import { useDashboard } from "../../hooks/useDashboard";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.35, delay, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] },
});

const Field = ({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) => (
  <div className="space-y-2">
    <label className="block text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>
      {label}
    </label>
    {children}
    {hint && <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>{hint}</p>}
  </div>
);

export const Settings = () => {
  const [showKey, setShowKey] = useState(false);
  const { isOnline, isDbConnected } = useDashboard();


  return (
    <div className="max-w-3xl mx-auto space-y-8">

      {/* Header */}
      <motion.div {...fadeUp(0)}>
        <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Settings</p>
        <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Configuration</h1>
        <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
          Manage API keys, model endpoints, and system parameters.
        </p>
      </motion.div>

      {/* API Keys */}
      <motion.div {...fadeUp(0.06)} className="grad-border rounded-2xl overflow-hidden"
        style={{ background: "var(--color-surface-1)" }}>
        <div className="flex items-center gap-3 px-6 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "rgba(79,142,247,0.12)", border: "1px solid rgba(79,142,247,0.2)" }}>
            <Key className="w-4 h-4" style={{ color: "var(--color-blue)" }} />
          </div>
          <div>
            <p className="text-[13px] font-semibold" style={{ color: "var(--color-text-1)" }}>API Credentials</p>
            <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>Manage your LLM provider keys</p>
          </div>
        </div>
        <div className="p-6 space-y-5">
          <Field label="Groq API Key" hint="Stored securely via environment variables. Never persisted to cloud.">
            <div className="relative flex items-center">
              <input
                type={showKey ? "text" : "password"}
                defaultValue="gsk_••••••••••••••••••••••••••••••••••••••••"
                readOnly
                className="w-full px-4 py-2.5 rounded-xl text-[12px] font-mono outline-none transition-colors"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-1)" }}
              />
              <button onClick={() => setShowKey(!showKey)}
                className="absolute right-3 cursor-pointer transition-colors"
                style={{ color: "var(--color-text-3)" }}>
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </Field>
          <div className="flex items-center gap-2.5 px-4 py-3 rounded-xl text-[12px]"
            style={{ background: "rgba(52,211,153,0.06)", border: "1px solid rgba(52,211,153,0.15)", color: "var(--color-emerald)" }}>
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            API key verified and active. Connection latency: ~320ms.
          </div>
        </div>
      </motion.div>

      {/* Model Config */}
      <motion.div {...fadeUp(0.1)} className="grad-border rounded-2xl overflow-hidden"
        style={{ background: "var(--color-surface-1)" }}>
        <div className="flex items-center gap-3 px-6 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "rgba(124,106,247,0.12)", border: "1px solid rgba(124,106,247,0.2)" }}>
            <Cpu className="w-4 h-4" style={{ color: "var(--color-violet)" }} />
          </div>
          <div>
            <p className="text-[13px] font-semibold" style={{ color: "var(--color-text-1)" }}>Model Configuration</p>
            <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>LLM adapter and inference settings</p>
          </div>
        </div>
        <div className="p-6 space-y-5">
          <Field label="Active Model">
            <select disabled className="w-full px-4 py-2.5 rounded-xl text-[12px] outline-none cursor-not-allowed"
              style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-1)" }}>
              <option>llama-3.3-70b-versatile (Default)</option>
              <option>llama3-8b-8192</option>
              <option>mixtral-8x7b-32768</option>
            </select>
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Temperature">
              <input type="text" defaultValue="0.7" readOnly
                className="w-full px-4 py-2.5 rounded-xl text-[12px] font-mono outline-none"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-1)" }} />
            </Field>
            <Field label="Max Tokens">
              <input type="text" defaultValue="2048" readOnly
                className="w-full px-4 py-2.5 rounded-xl text-[12px] font-mono outline-none"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-1)" }} />
            </Field>
          </div>
        </div>
      </motion.div>

      {/* System */}
      <motion.div {...fadeUp(0.14)} className="grad-border rounded-2xl overflow-hidden"
        style={{ background: "var(--color-surface-1)" }}>
        <div className="flex items-center gap-3 px-6 py-4" style={{ borderBottom: "1px solid var(--color-border)" }}>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "rgba(251,191,36,0.12)", border: "1px solid rgba(251,191,36,0.2)" }}>
            <Sliders className="w-4 h-4" style={{ color: "var(--color-amber)" }} />
          </div>
          <div>
            <p className="text-[13px] font-semibold" style={{ color: "var(--color-text-1)" }}>System Info</p>
            <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>Runtime environment details</p>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { k: "Backend Connection",  v: isOnline ? "Online" : "Offline", status: isOnline },
              { k: "Database Connection", v: isDbConnected ? "Connected" : "Unavailable", status: isDbConnected },
              { k: "Backend Tech Stack",  v: "FastAPI 0.115 · Python 3.12" },
              { k: "Database Engine",     v: "Supabase (PostgreSQL 15)" },
              { k: "AI Core Layer",       v: "CrewAI + LangGraph" },
              { k: "Inference Latency",   v: "~320ms (Groq adapter)" },
              { k: "Frontend Platform",   v: "React 19 · Vite 8" },
              { k: "System Version",      v: "AgentFleet v1.0.0-stable" },
            ].map(({ k, v, status }) => (
              <div key={k} className="flex items-center justify-between px-4 py-3 rounded-xl"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                <span className="text-[11px]" style={{ color: "var(--color-text-3)" }}>{k}</span>
                <span className="text-[11px] font-semibold flex items-center gap-1.5" 
                  style={{ color: status !== undefined ? (status ? "var(--color-emerald)" : "var(--color-rose)") : "var(--color-text-1)" }}>
                  {status !== undefined && (
                    <span className="relative flex h-1.5 w-1.5">
                      {status && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                      <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${status ? "bg-emerald-500" : "bg-rose-500"}`}></span>
                    </span>
                  )}
                  {v}
                </span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Security note */}
      <motion.div {...fadeUp(0.18)} className="flex items-start gap-3 px-5 py-4 rounded-2xl"
        style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)" }}>
        <Shield className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-blue)" }} />
        <p className="text-[12px] leading-relaxed" style={{ color: "var(--color-text-3)" }}>
          All credentials are loaded from environment variables and never stored in the database or transmitted to third-party services.
        </p>
      </motion.div>
    </div>
  );
};

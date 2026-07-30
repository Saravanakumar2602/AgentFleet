import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, RotateCcw, CheckCircle2, Loader2, Settings2, Navigation, 
  ShieldAlert, BarChart, Send, Sparkles, ClipboardCheck, TrafficCone,
  CloudSun, Timer, FileSpreadsheet, Fuel, Star, FileText, TrendingUp, AlertOctagon 
} from "lucide-react";

const STEPS = [
  { name: "Cargo Validation Agent", role: "Pre-flight Checker", icon: ClipboardCheck, color: "var(--color-blue)",    desc: "Validates cargo weight restrictions and hazard permit status." },
  { name: "Dispatch Agent",         role: "Fleet Assigner",     icon: Settings2,      color: "var(--color-blue)",    desc: "Allocates optimal vehicle and driver by cargo weight and availability." },
  { name: "Traffic Agent",          role: "Traffic Analyzer",   icon: TrafficCone,    color: "var(--color-violet)",  desc: "Analyzes route congestion patterns and time delays." },
  { name: "Weather Agent",          role: "Route Advisor",      icon: CloudSun,       color: "var(--color-violet)",  desc: "Fetches live weather conditions at destination using wttr.in." },
  { name: "Route Agent",            role: "Route Intelligence", icon: Navigation,     color: "var(--color-violet)",  desc: "Computes Haversine ETA, fuel estimate, and optimal path coordinates." },
  { name: "ETA Updater Agent",      role: "Precision Timer",    icon: Timer,          color: "var(--color-violet)",  desc: "Refines trip ETA based on live traffic and weather delays." },
  { name: "Compliance Agent",       role: "Regulatory Checker", icon: FileSpreadsheet, color: "var(--color-emerald)", desc: "Verifies driver work hours and vehicle compliance logs." },
  { name: "Maintenance Agent",      role: "Diagnostic Checker", icon: ShieldAlert,    color: "var(--color-emerald)", desc: "Validates vehicle health index and clears active DTC codes." },
  { name: "Fuel Agent",             role: "Fuel Planner",       icon: Fuel,           color: "var(--color-emerald)", desc: "Plans fuel stops and projects total transaction cost." },
  { name: "Analytics Agent",        role: "Data Aggregator",    icon: BarChart,       color: "var(--color-amber)",   desc: "Updates trip history, utilization indices, and fuel logs." },
  { name: "Driver Rating Agent",    role: "Performance Scorer", icon: Star,           color: "var(--color-amber)",   desc: "Scores driver history metrics and logs DB ratings." },
  { name: "Customer Agent",         role: "Notifier Service",   icon: Send,           color: "#f87171",              desc: "Generates ETA notifications and logs customer confirmations." },
  { name: "Invoice Agent",          role: "Billing Generator",  icon: FileText,       color: "#f87171",              desc: "Formats and sends a PDF-styled invoice to the customer." },
  { name: "Fleet Summary Agent",    role: "Fleet KPI Reporter", icon: TrendingUp,     color: "var(--color-blue)",    desc: "Aggregates overall fleet performance indexes." },
  { name: "SOS Alert Agent",        role: "Emergency Monitor",  icon: AlertOctagon,   color: "#ef4444",              desc: "Dispatches alerts on severe weather or low vehicle health." },
];

import { useWorkflow } from "../../hooks/useWorkflow";

export const Workflow = () => {
  const { steps, logs, isDone, isRunning, trigger, reset } = useWorkflow();

  const run = () => {
    if (isRunning || isDone) return;
    trigger({
      workflow: "fleet_delivery",
      pickup: "chennai",
      destination: "bangalore",
      weight: 2500,
    });
  };

  const isIdle = steps.every((s) => s.status === "idle");
  const activeIndex = steps.findIndex((s) => s.status === "running" || s.status === "failed");
  const active = isIdle ? -1 : activeIndex !== -1 ? activeIndex : steps.every((s) => s.status === "completed") ? steps.length : steps.filter((s) => s.status === "completed").length;
  const running = isRunning;
  const done = isDone;


  return (
    <div className="max-w-5xl mx-auto space-y-8">

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}
        className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Workflow Engine</p>
          <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Agent Orchestrator</h1>
          <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
            Sequential multi-agent pipeline execution with live telemetry.
          </p>
        </div>
        <div className="flex items-center gap-2.5 shrink-0">
          <button onClick={reset} disabled={running || active === -1}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold transition-all cursor-pointer disabled:opacity-30"
            style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)", color: "var(--color-text-2)" }}>
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
            onClick={run} disabled={running || done}
            className="flex items-center gap-2 px-5 py-2 rounded-xl text-[12px] font-semibold text-white transition-all cursor-pointer disabled:opacity-40"
            style={{ background: "linear-gradient(135deg, #4f8ef7, #7c6af7)", boxShadow: "0 4px 20px rgba(79,142,247,0.3)" }}>
            {running ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            {running ? "Running..." : done ? "Completed" : "Run Workflow"}
          </motion.button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

        {/* Pipeline — 3 cols */}
        <motion.div
          initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08, duration: 0.38 }}
          className="lg:col-span-3 grad-border rounded-2xl p-6 relative overflow-hidden min-h-[480px] flex flex-col"
          style={{ background: "var(--color-surface-1)" }}
        >
          {/* Idle overlay */}
          <AnimatePresence>
            {active === -1 && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="absolute inset-0 flex flex-col items-center justify-center z-10 rounded-2xl"
                style={{ background: "rgba(10,10,15,0.7)", backdropFilter: "blur(8px)" }}
              >
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-4"
                  style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                  <Sparkles className="w-5 h-5" style={{ color: "var(--color-violet)" }} />
                </div>
                <p className="text-[14px] font-semibold mb-1" style={{ color: "var(--color-text-1)" }}>Pipeline Idle</p>
                <p className="text-[12px]" style={{ color: "var(--color-text-3)" }}>Click Run Workflow to begin</p>
              </motion.div>
            )}
          </AnimatePresence>

          <p className="text-[11px] font-semibold uppercase tracking-widest mb-6" style={{ color: "var(--color-text-3)" }}>
            Execution Pipeline
          </p>

          <div className="flex-1 flex flex-col justify-between relative">
            {/* Connector track */}
            <div className="absolute left-[19px] top-5 bottom-5 w-px" style={{ background: "var(--color-border)" }} />

            {/* Animated progress fill */}
            {active >= 0 && (
              <motion.div
                className="absolute left-[19px] top-5 w-px origin-top animated-connector"
                initial={{ height: 0 }}
                animate={{ height: `${Math.min(100, (active / (STEPS.length - 1)) * 100)}%` }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              />
            )}

            {STEPS.map((step, i) => {
              const Icon = step.icon;
              const isCompleted = active > i;
              const isActive = active === i;
              const isPending = active < i;

              return (
                <div key={i} className="flex items-start gap-4 relative z-10">
                  {/* Node */}
                  <motion.div
                    animate={{
                      scale: isActive ? 1.15 : 1,
                      borderColor: isActive ? step.color : isCompleted ? "var(--color-emerald)" : "var(--color-border)",
                    }}
                    className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 border-2 relative ${isActive ? "glow-blue shadow-lg" : ""}`}
                    style={{ 
                      background: isCompleted ? "rgba(16, 185, 129, 0.08)" : isActive ? "rgba(59, 130, 246, 0.08)" : "var(--color-surface-2)",
                      boxShadow: isActive ? `0 0 20px -2px ${step.color}40` : undefined
                    }}
                  >
                    {isActive && (
                      <span className="absolute inset-0 rounded-full pulse-dot animate-pulse" style={{ color: step.color }} />
                    )}
                    {isCompleted
                      ? <CheckCircle2 className="w-4 h-4 relative z-10" style={{ color: "var(--color-emerald)" }} />
                      : isActive
                        ? <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="relative z-10">
                            <Icon className="w-4 h-4" style={{ color: step.color }} />
                          </motion.div>
                        : <Icon className="w-4 h-4 relative z-10" style={{ color: isPending ? "var(--color-text-3)" : step.color }} />
                    }
                  </motion.div>

                  {/* Content */}
                  <motion.div
                    animate={{ opacity: isPending ? 0.4 : 1 }}
                    className="flex-1 pb-6 last:pb-0"
                  >
                    <div className="flex items-center justify-between mb-0.5">
                      <p className="text-[13px] font-semibold" style={{ color: isActive ? step.color : isCompleted ? "var(--color-text-1)" : "var(--color-text-2)" }}>
                        {step.name}
                      </p>
                      <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md"
                        style={{ color: "var(--color-text-3)", background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                        {step.role}
                      </span>
                    </div>
                    <p className="text-[11px] leading-relaxed" style={{ color: "var(--color-text-3)" }}>
                      {steps[i]?.detail ? (
                        <span className="font-mono text-[var(--color-text-2)]">{steps[i].detail}</span>
                      ) : (
                        step.desc
                      )}
                    </p>
                    {isActive && (
                      <motion.div initial={{ opacity: 0, width: 0 }} animate={{ opacity: 1, width: "100%" }}
                        className="h-0.5 rounded-full mt-2" style={{ background: `linear-gradient(to right, ${step.color}, transparent)` }} />
                    )}

                  </motion.div>
                </div>
              );
            })}
          </div>

          {/* Done banner */}
          <AnimatePresence>
            {done && (
              <motion.div
                initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="mt-4 flex items-center gap-2 px-4 py-3 rounded-xl text-[12px] font-semibold"
                style={{ background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.2)", color: "var(--color-emerald)" }}
              >
                <CheckCircle2 className="w-4 h-4" />
                All 15 agents completed successfully. Transaction persisted.
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Terminal — 2 cols */}
        <motion.div
          initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.14, duration: 0.38 }}
          className="lg:col-span-2 grad-border rounded-2xl flex flex-col overflow-hidden"
          style={{ background: "var(--color-surface-1)", minHeight: 480 }}
        >
          {/* Terminal header */}
          <div className="flex items-center justify-between px-4 py-3 shrink-0"
            style={{ borderBottom: "1px solid var(--color-border)", background: "var(--color-surface-2)" }}>
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                {["#f87171","#fbbf24","#34d399"].map(c => (
                  <div key={c} className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
                ))}
              </div>
              <span className="text-[11px] font-semibold ml-2" style={{ color: "var(--color-text-3)" }}>orchestrator.log</span>
            </div>
            {running && (
              <motion.div animate={{ opacity: [1, 0.3, 1] }} transition={{ duration: 1, repeat: Infinity }}
                className="w-2 h-2 rounded-full" style={{ background: "var(--color-emerald)" }} />
            )}
          </div>

          {/* Log output */}
          <div className="flex-1 p-4 overflow-y-auto font-mono text-[11px] leading-relaxed space-y-1.5">
            {logs.length === 0
              ? <span style={{ color: "var(--color-text-3)" }}>$ awaiting workflow trigger...</span>
              : logs.map((log, i) => (
                <motion.div key={i}
                  initial={{ opacity: 0, x: -4 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  style={{
                    color: log.type === "success" ? "var(--color-emerald)"
                         : log.type === "info"    ? "var(--color-blue)"
                         : "var(--color-text-2)",
                  }}
                >
                  {log.text}
                </motion.div>
              ))
            }
            {running && (
              <motion.span animate={{ opacity: [1, 0] }} transition={{ duration: 0.8, repeat: Infinity }}
                style={{ color: "var(--color-text-3)" }}>▋</motion.span>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

import { useEffect } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Sparkles, Activity, Play, ArrowRight, ShieldCheck,
  AlertCircle, Zap, GitFork, MessageSquare, Truck,
  CheckCircle2, Clock, TrendingUp, WifiOff, RefreshCw,
} from "lucide-react";
import { useDashboard } from "../../hooks/useDashboard";
import { useToast } from "../../context/ToastContext";
import { Skeleton } from "../../components/ui/Skeleton";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, delay, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] },
});

/* ── Fleet Health Ring ── */
const HealthRing = ({ score }: { score: number }) => {
  const r = 52, sw = 7;
  const nr = r - sw * 2;
  const circ = nr * 2 * Math.PI;
  const offset = circ - (score / 100) * circ;
  return (
    <div className="relative flex items-center justify-center" style={{ width: r * 2, height: r * 2 }}>
      <svg width={r * 2} height={r * 2} className="-rotate-90">
        <defs>
          <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4f8ef7" />
            <stop offset="100%" stopColor="#7c6af7" />
          </linearGradient>
        </defs>
        <circle stroke="var(--color-border)" fill="transparent" strokeWidth={sw} r={nr} cx={r} cy={r} />
        <motion.circle
          stroke="url(#ring-grad)" fill="transparent" strokeWidth={sw}
          strokeDasharray={`${circ} ${circ}`} strokeLinecap="round"
          r={nr} cx={r} cy={r}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.4, delay: 0.3, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-xl font-black" style={{ color: "var(--color-text-1)" }}>{score}%</span>
        <span className="text-[9px] font-semibold uppercase tracking-widest mt-0.5" style={{ color: "var(--color-text-3)" }}>Health</span>
      </div>
    </div>
  );
};

const StatPill = ({ label, value, delta, color }: { label: string; value: string; delta?: string; color: string }) => (
  <div className="flex flex-col gap-1">
    <span className="text-[11px] font-medium" style={{ color: "var(--color-text-3)" }}>{label}</span>
    <div className="flex items-baseline gap-2">
      <span className="text-2xl font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>{value}</span>
      {delta && (
        <span className="text-[11px] font-semibold px-1.5 py-0.5 rounded-md" style={{ color, background: `${color}18` }}>
          {delta}
        </span>
      )}
    </div>
  </div>
);

const ACTIVITY = [
  { icon: CheckCircle2, color: "var(--color-emerald)", title: "Dispatch Completed", desc: "Vehicle TN38AB1234 → Ravi K. assigned Chennai–Coimbatore (2.5t)", time: "10:14 AM" },
  { icon: Sparkles,     color: "var(--color-blue)",    title: "Intent Classified",  desc: "Supervisor parsed \"fleet_delivery\" from natural language query", time: "10:14 AM" },
  { icon: Zap,          color: "var(--color-amber)",   title: "Route Optimized",    desc: "Haversine ETA computed: 4h 22m · 312 km · 28.4L fuel estimate", time: "10:12 AM" },
  { icon: ShieldCheck,  color: "var(--color-violet)",  title: "Health Check Passed", desc: "All 9 vehicles cleared diagnostics. Zero critical DTCs active", time: "09:58 AM" },
];

const QUICK_ACTIONS = [
  { to: "/workflow", icon: Play,          label: "Trigger Workflow",  color: "var(--color-blue)" },
  { to: "/chat",     icon: MessageSquare, label: "Open AI Chat",      color: "var(--color-violet)" },
  { to: "/fleet",    icon: Truck,         label: "Fleet Registry",    color: "var(--color-emerald)" },
  { to: "/analytics",icon: TrendingUp,    label: "View Analytics",    color: "var(--color-amber)" },
];

export const Dashboard = () => {
  const { isOnline, isDbConnected, stats, isLoading, isError, error, refetch } = useDashboard();
  const { toast } = useToast();

  useEffect(() => {
    if (isError && error) {
      toast("error", (error as Error).message ?? "Backend unreachable.", refetch);
    }
  }, [isError, error, toast, refetch]);

  const systemStatus = isLoading
    ? "Connecting..."
    : isError
    ? "Backend offline"
    : isOnline
    ? "All systems operational"
    : "Degraded";

  const statusColor = isLoading
    ? "var(--color-text-3)"
    : isError
    ? "var(--color-rose)"
    : "var(--color-emerald)";

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* ── Hero Header ── */}
      <motion.div 
        {...fadeUp(0)} 
        className="hero-grid noise grad-border rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden"
        style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)" }}
      >
        <div className="absolute top-0 right-0 w-80 h-80 rounded-full pointer-events-none filter blur-[100px]"
          style={{ background: "radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)" }} />
        <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full pointer-events-none filter blur-[100px]"
          style={{ background: "radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 70%)" }} />

        <div className="relative z-10 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-[var(--color-blue-light)]">
              Enterprise Fleet Intelligence Platform
            </span>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <h1 className="text-[28px] md:text-[32px] font-extrabold tracking-tight leading-none bg-gradient-to-r from-white via-zinc-100 to-zinc-400 bg-clip-text text-transparent">
            Good morning, Admin.
          </h1>
          <p className="text-[13px] leading-relaxed max-w-lg text-[var(--color-text-2)]">
            Your autonomous agent network is operating at peak efficiency. **{stats?.activeVehicles ?? 9} active vehicles** resolved via diagnostic supervisor.
          </p>
        </div>

        <div className="relative z-10 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0 w-full sm:w-auto">
          <div
            className="flex items-center justify-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-semibold shrink-0"
            style={{ background: `${statusColor}12`, border: `1px solid ${statusColor}28`, color: statusColor }}
            aria-live="polite"
          >
            {isError ? <WifiOff className="w-3.5 h-3.5" /> : <Activity className="w-3.5 h-3.5 animate-pulse" />}
            {systemStatus}
          </div>
          <button 
            onClick={() => refetch()}
            className="flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded-full text-[11px] font-semibold bg-zinc-900/60 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all cursor-pointer text-[var(--color-text-2)] hover:text-white"
          >
            <RefreshCw className="w-3 h-3" />
            Sync Metrics
          </button>
        </div>
      </motion.div>

      {/* ── Top Stats Row ── */}
      <motion.div {...fadeUp(0.06)} className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Active Vehicles",  value: stats ? String(stats.activeVehicles) : "9",      delta: stats?.activeVehiclesDelta ?? "+2",    color: "var(--color-emerald)" },
          { label: "Trips Today",      value: stats ? String(stats.tripsToday) : "14",         delta: stats?.tripsTodayDelta ?? "+5",    color: "var(--color-blue)" },
          { label: "Fuel Saved",       value: stats?.fuelSaved ?? "1,240L",                    delta: stats?.fuelSavedDelta ?? "−12%",  color: "var(--color-amber)" },
          { label: "Avg ETA Accuracy", value: stats?.avgEtaAccuracy ?? "97.3%",                delta: stats?.avgEtaAccuracyDelta ?? "+1.2%", color: "var(--color-violet)" },
        ].map((s) => (
          <motion.div 
            key={s.label} 
            whileHover={{ y: -3, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 400, damping: 28 }}
            className="grad-border rounded-xl p-5 relative overflow-hidden cursor-default group"
            style={{ background: "var(--color-surface-1)" }}
          >
            {isLoading ? (
              <div className="flex flex-col gap-2">
                <Skeleton className="h-2.5 w-24" />
                <Skeleton className="h-7 w-16" />
              </div>
            ) : (
              <StatPill {...s} />
            )}
          </motion.div>
        ))}
      </motion.div>

      {/* ── Main 3-col Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Fleet Health */}
        <motion.div 
          {...fadeUp(0.1)} 
          whileHover={{ y: -4, scale: 1.005 }}
          transition={{ type: "spring", stiffness: 450, damping: 32 }}
          className="grad-border rounded-2xl p-6 flex flex-col gap-5 relative overflow-hidden cursor-default"
          style={{ background: "var(--color-surface-1)" }}
        >
          <div className="absolute -top-10 -left-10 w-40 h-40 rounded-full pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(79,142,247,0.12) 0%, transparent 70%)" }} />
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Fleet Health</p>
            <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Real-time diagnostics</p>
          </div>
          <div className="flex items-center gap-6">
            {isLoading ? (
              <Skeleton className="w-[104px] h-[104px] rounded-full" />
            ) : (
              <HealthRing score={stats?.fleetHealthScore ?? 92} />
            )}
            <div className="space-y-3.5">
              <div className="flex items-start gap-2.5">
                <ShieldCheck className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-emerald)" }} />
                <div>
                  {isLoading ? (
                    <Skeleton className="h-4 w-24" />
                  ) : (
                    <>
                      <p className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>
                        {stats?.operationalVehiclesCount ?? 9} Operational
                      </p>
                      <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>Vehicles active</p>
                    </>
                  )}
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" style={{ color: "var(--color-amber)" }} />
                <div>
                  {isLoading ? (
                    <Skeleton className="h-4 w-24" />
                  ) : (
                    <>
                      <p className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>
                        {stats?.serviceDueCount ?? 1} Service Due
                      </p>
                      <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>Scheduled maintenance</p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
          <p className="text-[11px] pt-4 leading-relaxed" style={{ color: "var(--color-text-3)", borderTop: "1px solid var(--color-border)" }}>
            Zero critical DTCs. All diagnostic endpoints nominal.
          </p>
        </motion.div>


        {/* AI Supervisor — live backend status */}
        <motion.div 
          {...fadeUp(0.14)} 
          whileHover={{ y: -4, scale: 1.005 }}
          transition={{ type: "spring", stiffness: 450, damping: 32 }}
          className="grad-border rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden cursor-default"
          style={{ background: "var(--color-surface-1)" }}
        >
          <div className="absolute -top-8 -right-8 w-36 h-36 rounded-full pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(124,106,247,0.12) 0%, transparent 70%)" }} />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>AI Supervisor</p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>LLM orchestration core</p>
            </div>
            <div className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, rgba(79,142,247,0.2), rgba(124,106,247,0.2))", border: "1px solid rgba(124,106,247,0.25)" }}>
              <Sparkles className="w-4 h-4" style={{ color: "var(--color-violet)" }} />
            </div>
          </div>
          <div className="space-y-2.5 flex-1">
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between py-2" style={{ borderBottom: "1px solid var(--color-border-subtle)" }}>
                  <Skeleton className="h-2.5 w-20" />
                  <Skeleton className="h-2.5 w-28" />
                </div>
              ))
            ) : (
              [
                { k: "Model",    v: "llama-3.3-70b-versatile", highlight: false },
                { k: "Adapter",  v: "Groq SDK",                highlight: true },
                { k: "Backend",  v: isOnline ? "Online" : "Offline", highlight: isOnline },
                { k: "Database", v: isDbConnected ? "Connected" : "Unavailable", highlight: isDbConnected },
              ].map(({ k, v, highlight }) => (
                <div key={k} className="flex items-center justify-between py-2"
                  style={{ borderBottom: "1px solid var(--color-border-subtle)" }}>
                  <span className="text-[12px]" style={{ color: "var(--color-text-3)" }}>{k}</span>
                  <span className={`text-[12px] font-semibold ${highlight ? "px-2 py-0.5 rounded-md" : ""}`}
                    style={highlight
                      ? { color: "var(--color-emerald)", background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)" }
                      : { color: "var(--color-text-1)" }}>
                    {v}
                  </span>
                </div>
              ))
            )}
          </div>
          <Link to="/chat">
            <button className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-[12px] font-semibold transition-all cursor-pointer hover:opacity-90"
              style={{ background: "linear-gradient(135deg, rgba(79,142,247,0.15), rgba(124,106,247,0.15))", border: "1px solid rgba(124,106,247,0.25)", color: "var(--color-text-1)" }}>
              <MessageSquare className="w-3.5 h-3.5" />
              Open Chat Interface
            </button>
          </Link>
        </motion.div>

        {/* Workflow Status */}
        <motion.div 
          {...fadeUp(0.18)} 
          whileHover={{ y: -4, scale: 1.005 }}
          transition={{ type: "spring", stiffness: 450, damping: 32 }}
          className="grad-border rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden cursor-default"
          style={{ background: "var(--color-surface-1)" }}
        >
          <div className="absolute -bottom-8 -right-8 w-36 h-36 rounded-full pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(79,142,247,0.08) 0%, transparent 70%)" }} />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Workflow Engine</p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Orchestration status</p>
            </div>
            <GitFork className="w-4 h-4" style={{ color: "var(--color-blue)" }} />
          </div>
          <div className="space-y-2.5 flex-1">
            {[
              { k: "Last Run",      v: "On demand",  ok: true },
              { k: "Success Rate",  v: "100%",       ok: true },
              { k: "Agents Active", v: "5 / 5",      ok: true },
              { k: "Rollback",      v: "Secure",     ok: true },
            ].map(({ k, v, ok }) => (
              <div key={k} className="flex items-center justify-between py-2"
                style={{ borderBottom: "1px solid var(--color-border-subtle)" }}>
                <span className="text-[12px]" style={{ color: "var(--color-text-3)" }}>{k}</span>
                <div className="flex items-center gap-1.5">
                  {ok && <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--color-emerald)" }} />}
                  <span className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>{v}</span>
                </div>
              </div>
            ))}
          </div>
          <Link to="/workflow">
            <button className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-[12px] font-semibold transition-all cursor-pointer hover:opacity-90"
              style={{ background: "rgba(79,142,247,0.12)", border: "1px solid rgba(79,142,247,0.2)", color: "var(--color-text-1)" }}>
              <Play className="w-3.5 h-3.5" style={{ color: "var(--color-blue)" }} />
              Run Workflow
            </button>
          </Link>
        </motion.div>
      </div>

      {/* ── Bottom: Activity + Quick Actions ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Activity Feed */}
        <motion.div 
          {...fadeUp(0.22)} 
          whileHover={{ y: -4, scale: 1.005 }}
          transition={{ type: "spring", stiffness: 450, damping: 32 }}
          className="lg:col-span-2 grad-border rounded-2xl p-6 flex flex-col gap-5 cursor-default"
          style={{ background: "var(--color-surface-1)" }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Recent Activity</p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Live system event stream</p>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-semibold" style={{ color: "var(--color-emerald)" }}>
              <span className="relative w-2 h-2">
                <span className="absolute inset-0 rounded-full animate-ping" style={{ background: "var(--color-emerald)", opacity: 0.4 }} />
                <span className="relative block w-2 h-2 rounded-full" style={{ background: "var(--color-emerald)" }} />
              </span>
              Live
            </div>
          </div>
          <div className="space-y-1">
            {ACTIVITY.map(({ icon: Icon, color, title, desc, time }, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.28 + i * 0.07, duration: 0.3, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
                className="flex items-start gap-3.5 p-3 rounded-xl transition-colors group cursor-default"
                style={{ borderBottom: i < ACTIVITY.length - 1 ? "1px solid var(--color-border-subtle)" : "none" }}
              >
                <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: `${color}18`, border: `1px solid ${color}30` }}>
                  <Icon className="w-3.5 h-3.5" style={{ color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>{title}</p>
                  <p className="text-[11px] mt-0.5 leading-relaxed" style={{ color: "var(--color-text-3)" }}>{desc}</p>
                </div>
                <span className="text-[10px] font-medium shrink-0 mt-0.5" style={{ color: "var(--color-text-3)" }}>{time}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div 
          {...fadeUp(0.26)} 
          whileHover={{ y: -4, scale: 1.005 }}
          transition={{ type: "spring", stiffness: 450, damping: 32 }}
          className="grad-border rounded-2xl p-6 flex flex-col gap-4 cursor-default"
          style={{ background: "var(--color-surface-1)" }}
        >
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Quick Actions</p>
            <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Jump to key workflows</p>
          </div>
          <div className="flex flex-col gap-2 flex-1">
            {QUICK_ACTIONS.map(({ to, icon: Icon, label, color }) => (
              <Link key={to} to={to}>
                <motion.div
                  whileHover={{ x: 3 }}
                  transition={{ type: "spring", stiffness: 400, damping: 28 }}
                  className="flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer group transition-colors"
                  style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                      style={{ background: `${color}18`, border: `1px solid ${color}28` }}>
                      <Icon className="w-3.5 h-3.5" style={{ color }} />
                    </div>
                    <span className="text-[12px] font-medium" style={{ color: "var(--color-text-1)" }}>{label}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5"
                    style={{ color: "var(--color-text-3)" }} />
                </motion.div>
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-2 p-3 rounded-xl text-[11px]"
            style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-3)" }}>
            <Clock className="w-3.5 h-3.5 shrink-0" />
            {isLoading ? "Checking backend status..." : isOnline ? "Backend online · All agents healthy." : "Backend unreachable — check server."}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

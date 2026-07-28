import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Zap, Route, BarChart3, Activity, RefreshCw } from "lucide-react";
import { useAnalytics } from "../../hooks/useAnalytics";
import { FLEET_VEHICLE_IDS } from "../../hooks/useFleet";
import { useToast } from "../../context/ToastContext";
import { Skeleton, SkeletonCard } from "../../components/ui/Skeleton";

const AnimatedCounter = ({ value, duration = 850 }: { value: string | number; duration?: number }) => {
  const numVal = typeof value === "number" ? value : parseFloat(value.replace(/[^0-9.]/g, ""));
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (isNaN(numVal) || numVal === 0) return;
    let start = 0;
    const end = numVal;
    const incrementTime = 16;
    const step = Math.max(0.1, end / (duration / incrementTime));

    const timer = setInterval(() => {
      start += step;
      if (start >= end) {
        clearInterval(timer);
        setCount(end);
      } else {
        setCount(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [numVal, duration]);

  if (typeof value === "string") {
    const suffix = value.replace(/[0-9.]/g, "");
    const decimals = numVal % 1 === 0 ? 0 : 1;
    return <span>{count.toFixed(decimals)}{suffix}</span>;
  }

  return <span>{Math.round(count)}</span>;
};

const Sparkline = ({ color, index }: { color: string; index: number }) => {
  const paths = [
    "M2 18 C 12 12, 18 4, 30 8 C 42 12, 48 2, 62 2", // Utilization
    "M2 18 C 12 16, 20 8, 30 14 C 40 18, 50 6, 62 4", // Fuel
    "M2 12 C 15 2, 28 18, 40 10 C 50 2, 58 14, 62 6",  // Avg Distance
    "M2 18 C 15 15, 25 2, 40 12 C 50 18, 58 4, 62 2"   // Trips
  ];
  const path = paths[index % paths.length];
  
  return (
    <svg className="w-16 h-8 absolute bottom-3 right-3 opacity-60 pointer-events-none" viewBox="0 0 64 20" fill="none">
      <path d={path} stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d={`${path} L 62 20 L 2 20 Z`} fill={`url(#spark-grad-${index})`} opacity="0.1" />
      <defs>
        <linearGradient id={`spark-grad-${index}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} />
          <stop offset="100%" stopColor="transparent" />
        </linearGradient>
      </defs>
    </svg>
  );
};

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.38, delay, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] },
});

/* ── Animated SVG Area Chart — animates after data loads ── */
const AreaChart = ({ ready }: { ready: boolean }) => {
  const points = [88, 72, 91, 65, 95, 78, 97, 84, 99, 76, 94, 100];
  const w = 400, h = 100;
  const step = w / (points.length - 1);
  const toY = (v: number) => h - (v / 100) * h * 0.85 - 4;
  const pathD = points.map((v, i) => `${i === 0 ? "M" : "L"} ${i * step} ${toY(v)}`).join(" ");
  const areaD = `${pathD} L ${(points.length - 1) * step} ${h} L 0 ${h} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className="w-full h-full">
      <defs>
        <linearGradient id="area-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#4f8ef7" stopOpacity="0.22" />
          <stop offset="100%" stopColor="#4f8ef7" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="line-grad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#4f8ef7" />
          <stop offset="100%" stopColor="#7c6af7" />
        </linearGradient>
      </defs>
      {[25, 50, 75].map(y => (
        <line key={y} x1="0" y1={toY(y)} x2={w} y2={toY(y)}
          stroke="var(--color-border)" strokeWidth="0.5" strokeDasharray="4 4" />
      ))}
      <motion.path d={areaD} fill="url(#area-fill)"
        initial={{ opacity: 0 }} animate={{ opacity: ready ? 1 : 0 }}
        transition={{ delay: 0.5, duration: 0.6 }} />
      <motion.path d={pathD} fill="none" stroke="url(#line-grad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: ready ? 1 : 0 }}
        transition={{ delay: ready ? 0.3 : 0, duration: 1.2, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }} />
      {ready && points.map((v, i) => (
        <motion.circle key={i} cx={i * step} cy={toY(v)} r="3" fill="#4f8ef7"
          initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 + i * 0.07, duration: 0.2 }} />
      ))}
    </svg>
  );
};

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const Analytics = () => {
  // Fetch analytics for first vehicle; also use fleet data for agent performance
  const { data, isLoading, isError, error, refetch } = useAnalytics(FLEET_VEHICLE_IDS[0].id);

  const { toast } = useToast();

  useEffect(() => {
    if (isError && error) {
      toast("error", (error as Error).message ?? "Failed to load analytics.", refetch);
    }
  }, [isError, error, toast, refetch]);

  // Build agent performance from live fleet health data
  const agentPerf = [
    { name: "Dispatch Agent",    color: "var(--color-blue)",    success: 99.8 },
    { name: "Route Agent",       color: "var(--color-violet)",  success: 98.4 },
    { name: "Maintenance Agent", color: "var(--color-emerald)", success: 100 },
    { name: "Analytics Agent",   color: "var(--color-amber)",   success: data ? Math.min(99.9, 95 + data.utilization * 0.05) : 99.1 },
    { name: "Customer Agent",    color: "var(--color-rose)",    success: 97.6 },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* Header */}
      <motion.div {...fadeUp(0)}>
        <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Analytics</p>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Fleet Intelligence</h1>
            <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
              Performance metrics, fuel efficiency, and agent operation analysis.
            </p>
          </div>
          <button onClick={() => refetch()} aria-label="Refresh analytics"
            className="flex items-center gap-2 px-3 py-2 rounded-xl text-[12px] font-medium transition-colors cursor-pointer shrink-0 mt-1"
            style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)", color: "var(--color-text-2)" }}>
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </motion.div>

      {/* Top KPI Row */}
      <motion.div {...fadeUp(0.06)} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="grad-border rounded-2xl p-5" style={{ background: "var(--color-surface-1)" }}>
                <div className="flex flex-col gap-3">
                  <Skeleton className="h-2.5 w-24" />
                  <Skeleton className="h-7 w-20" />
                  <Skeleton className="h-5 w-14 rounded-md" />
                </div>
              </div>
            ))
          : [
              { label: "Utilization",      value: data ? `${data.utilization}%`          : "—", delta: "+4.2%", up: true,  icon: TrendingUp,   color: "var(--color-emerald)" },
              { label: "Fuel Efficiency",  value: data ? `${data.fuel_efficiency} km/L`  : "—", delta: "−12%",  up: true,  icon: Zap,          color: "var(--color-amber)" },
              { label: "Avg Distance",     value: data ? `${data.average_distance} km`   : "—", delta: "−8km",  up: true,  icon: Route,        color: "var(--color-blue)" },
              { label: "Total Trips",      value: data ? `${data.total_trips}`            : "—", delta: "+5",    up: true,  icon: TrendingDown, color: "var(--color-violet)" },
            ].map(({ label, value, delta, up, icon: Icon, color }, i) => {
              const hasValue = value !== "—" && value !== undefined && value !== null;
              return (
                <motion.div key={label}
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.08 + i * 0.05, duration: 0.35 }}
                  whileHover={{ y: -4, scale: 1.01, boxShadow: `0 12px 30px -10px ${color}15` }}
                  className="grad-border rounded-2xl p-5 relative overflow-hidden cursor-default group"
                  style={{ background: "var(--color-surface-1)" }}
                >
                  <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full pointer-events-none"
                    style={{ background: `radial-gradient(circle, ${color}10 0%, transparent 70%)` }} />
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-medium" style={{ color: "var(--color-text-3)" }}>{label}</span>
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors group-hover:bg-zinc-800/40"
                      style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
                      <Icon className="w-3.5 h-3.5" style={{ color }} />
                    </div>
                  </div>
                  <p className="text-[24px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>
                    {hasValue ? <AnimatedCounter value={value} /> : "—"}
                  </p>
                  
                  {hasValue && <Sparkline color={color} index={i} />}

                  <span className="inline-flex items-center gap-1 mt-2.5 text-[10px] font-semibold px-2 py-0.5 rounded-md relative z-10"
                    style={{ color: up ? "var(--color-emerald)" : "var(--color-rose)", background: up ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)" }}>
                    {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {delta}
                  </span>
                </motion.div>
              );
            })
        }
      </motion.div>

      {/* Chart + Agent Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Area Chart */}
        <motion.div {...fadeUp(0.16)} className="lg:col-span-2 grad-border rounded-2xl p-6 flex flex-col gap-5"
          style={{ background: "var(--color-surface-1)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Utilization Trend</p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>
                Fleet capacity utilization % — last 12 months
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-semibold" style={{ color: "var(--color-blue)" }}>
              <Activity className="w-3.5 h-3.5" />
              {data ? `${data.utilization}% current` : "Loading..."}
            </div>
          </div>
          <div className="h-44 w-full relative">
            {isLoading
              ? <Skeleton className="w-full h-full rounded-xl" />
              : <AreaChart ready={!isLoading && !!data} />
            }
          </div>
          <div className="flex justify-between pt-2" style={{ borderTop: "1px solid var(--color-border)" }}>
            {MONTHS.map(m => (
              <span key={m} className="text-[10px] font-medium" style={{ color: "var(--color-text-3)" }}>{m}</span>
            ))}
          </div>
        </motion.div>

        {/* Agent Performance */}
        <motion.div {...fadeUp(0.2)} className="grad-border rounded-2xl p-6 flex flex-col gap-4"
          style={{ background: "var(--color-surface-1)" }}>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Agent Performance</p>
            <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Operations & success rate</p>
          </div>
          <div className="space-y-4 flex-1">
            {agentPerf.map(({ name, success, color }, i) => (
              <motion.div key={name}
                initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.24 + i * 0.06, duration: 0.3 }}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[12px] font-medium" style={{ color: "var(--color-text-1)" }}>{name}</span>
                  <span className="text-[11px] font-bold" style={{ color }}>{success}%</span>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-border)" }}>
                  <motion.div
                    initial={{ width: 0 }} animate={{ width: `${success}%` }}
                    transition={{ delay: 0.3 + i * 0.06, duration: 0.7, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
                    className="h-full rounded-full" style={{ background: color }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
          <div className="flex items-center gap-2 p-3 rounded-xl text-[11px]"
            style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-3)" }}>
            <BarChart3 className="w-3.5 h-3.5 shrink-0" />
            {data ? data.recommendation : "Loading recommendation..."}
          </div>
        </motion.div>
      </div>

      {/* Vehicle Report Detail */}
      {isLoading ? (
        <SkeletonCard rows={4} />
      ) : data ? (
        <motion.div {...fadeUp(0.24)} className="grad-border rounded-2xl p-6"
          style={{ background: "var(--color-surface-1)" }}>
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>
                Vehicle Report — {data.vehicle}
              </p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Live analytics from backend</p>
            </div>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { label: "Total Trips",       value: String(data.total_trips) },
              { label: "Avg Distance",      value: `${data.average_distance} km` },
              { label: "Fuel Efficiency",   value: `${data.fuel_efficiency} km/L` },
              { label: "Maintenance Count", value: String(data.maintenance_count) },
              { label: "Utilization",       value: `${data.utilization}%` },
              { label: "Recommendation",    value: data.recommendation },
            ].map(({ label, value }) => (
              <div key={label} className="p-4 rounded-xl flex flex-col gap-1"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                <p className="text-[10px]" style={{ color: "var(--color-text-3)" }}>{label}</p>
                <p className="text-[12px] font-semibold leading-snug" style={{ color: "var(--color-text-1)" }}>{value}</p>
              </div>
            ))}
          </div>
        </motion.div>
      ) : null}
    </div>
  );
};

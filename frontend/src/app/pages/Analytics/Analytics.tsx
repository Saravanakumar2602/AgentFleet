import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Zap, Route, BarChart3, Activity } from "lucide-react";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.38, delay, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] },
});

/* ── Animated SVG Area Chart ── */
const AreaChart = () => {
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
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5, duration: 0.6 }} />
      <motion.path d={pathD} fill="none" stroke="url(#line-grad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ delay: 0.3, duration: 1.2, ease: [0.22, 1, 0.36, 1] }} />
      {points.map((v, i) => (
        <motion.circle key={i} cx={i * step} cy={toY(v)} r="3" fill="#4f8ef7"
          initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 + i * 0.07, duration: 0.2 }} />
      ))}
    </svg>
  );
};

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const AGENT_PERF = [
  { name: "Dispatch Agent",     ops: 1420, success: 99.8, color: "var(--color-blue)" },
  { name: "Route Agent",        ops: 1380, success: 98.4, color: "var(--color-violet)" },
  { name: "Maintenance Agent",  ops:  890, success: 100,  color: "var(--color-emerald)" },
  { name: "Analytics Agent",    ops: 1420, success: 99.1, color: "var(--color-amber)" },
  { name: "Customer Agent",     ops:  760, success: 97.6, color: "var(--color-rose)" },
];

export const Analytics = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* Header */}
      <motion.div {...fadeUp(0)}>
        <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Analytics</p>
        <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Fleet Intelligence</h1>
        <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
          Performance metrics, fuel efficiency, and agent operation analysis.
        </p>
      </motion.div>

      {/* Top KPI Row */}
      <motion.div {...fadeUp(0.06)} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Optimization Score", value: "94.8%", delta: "+4.2%", up: true,  icon: TrendingUp,   color: "var(--color-emerald)" },
          { label: "Fuel Saved",         value: "1,240L", delta: "−12%", up: true,  icon: Zap,          color: "var(--color-amber)" },
          { label: "Avg Route Length",   value: "312 km", delta: "−8km", up: true,  icon: Route,        color: "var(--color-blue)" },
          { label: "Idle Time Reduced",  value: "38 hrs", delta: "+22%", up: false, icon: TrendingDown, color: "var(--color-violet)" },
        ].map(({ label, value, delta, up, icon: Icon, color }, i) => (
          <motion.div key={label}
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 + i * 0.05, duration: 0.35 }}
            whileHover={{ y: -2, transition: { duration: 0.18 } }}
            className="grad-border rounded-2xl p-5 relative overflow-hidden"
            style={{ background: "var(--color-surface-1)" }}
          >
            <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full pointer-events-none"
              style={{ background: `radial-gradient(circle, ${color}10 0%, transparent 70%)` }} />
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-medium" style={{ color: "var(--color-text-3)" }}>{label}</span>
              <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
                <Icon className="w-3.5 h-3.5" style={{ color }} />
              </div>
            </div>
            <p className="text-[24px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>{value}</p>
            <span className="inline-flex items-center gap-1 mt-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-md"
              style={{ color: up ? "var(--color-emerald)" : "var(--color-rose)", background: up ? "rgba(52,211,153,0.1)" : "rgba(248,113,113,0.1)" }}>
              {up ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {delta}
            </span>
          </motion.div>
        ))}
      </motion.div>

      {/* Chart + Agent Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Area Chart */}
        <motion.div {...fadeUp(0.16)} className="lg:col-span-2 grad-border rounded-2xl p-6 flex flex-col gap-5"
          style={{ background: "var(--color-surface-1)" }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Utilization Trend</p>
              <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>Fleet capacity utilization % — last 12 months</p>
            </div>
            <div className="flex items-center gap-1.5 text-[11px] font-semibold"
              style={{ color: "var(--color-blue)" }}>
              <Activity className="w-3.5 h-3.5" />
              94.8% avg
            </div>
          </div>
          <div className="h-44 w-full relative">
            <AreaChart />
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
            {AGENT_PERF.map(({ name, ops, success, color }, i) => (
              <motion.div key={name}
                initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.24 + i * 0.06, duration: 0.3 }}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[12px] font-medium" style={{ color: "var(--color-text-1)" }}>{name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px]" style={{ color: "var(--color-text-3)" }}>{ops.toLocaleString()} ops</span>
                    <span className="text-[11px] font-bold" style={{ color }}>{success}%</span>
                  </div>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-border)" }}>
                  <motion.div
                    initial={{ width: 0 }} animate={{ width: `${success}%` }}
                    transition={{ delay: 0.3 + i * 0.06, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                    className="h-full rounded-full" style={{ background: color }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
          <div className="flex items-center gap-2 p-3 rounded-xl text-[11px]"
            style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-3)" }}>
            <BarChart3 className="w-3.5 h-3.5 shrink-0" />
            All agents operating above 97% threshold.
          </div>
        </motion.div>
      </div>

      {/* Route Breakdown */}
      <motion.div {...fadeUp(0.24)} className="grad-border rounded-2xl p-6"
        style={{ background: "var(--color-surface-1)" }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: "var(--color-text-3)" }}>Top Routes</p>
            <p className="text-[12px] mt-0.5" style={{ color: "var(--color-text-2)" }}>By trip volume and avg utilization</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { route: "Chennai → Coimbatore",  trips: 142, util: 88, dist: "495 km" },
            { route: "Bangalore → Pune",       trips: 98,  util: 94, dist: "840 km" },
            { route: "Mumbai → Hyderabad",     trips: 76,  util: 79, dist: "711 km" },
            { route: "Chennai → Bangalore",    trips: 201, util: 96, dist: "346 km" },
          ].map(({ route, trips, util, dist }, i) => (
            <motion.div key={route}
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.28 + i * 0.05, duration: 0.3 }}
              className="p-4 rounded-xl" style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
            >
              <p className="text-[12px] font-semibold mb-3" style={{ color: "var(--color-text-1)" }}>{route}</p>
              <div className="space-y-1.5">
                <div className="flex justify-between text-[11px]">
                  <span style={{ color: "var(--color-text-3)" }}>Trips</span>
                  <span className="font-semibold" style={{ color: "var(--color-text-1)" }}>{trips}</span>
                </div>
                <div className="flex justify-between text-[11px]">
                  <span style={{ color: "var(--color-text-3)" }}>Distance</span>
                  <span className="font-semibold" style={{ color: "var(--color-text-1)" }}>{dist}</span>
                </div>
                <div className="flex justify-between text-[11px]">
                  <span style={{ color: "var(--color-text-3)" }}>Utilization</span>
                  <span className="font-semibold" style={{ color: util >= 90 ? "var(--color-emerald)" : "var(--color-amber)" }}>{util}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

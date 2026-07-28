import { motion } from "framer-motion";
import { Truck, ShieldCheck, Wrench, AlertTriangle, MapPin, Weight, User } from "lucide-react";

interface Vehicle {
  id: string; type: string; capacity: string;
  status: "Available" | "In Transit" | "Maintenance";
  driver: string; route?: string; health: number;
}

const FLEET: Vehicle[] = [
  { id: "TN38AB1234", type: "Dry Van",     capacity: "3,000 kg", status: "Available",  driver: "Ravi K.",   health: 98 },
  { id: "TN38CD5678", type: "Flatbed",     capacity: "5,000 kg", status: "In Transit", driver: "Suresh P.", route: "Chennai → Coimbatore", health: 91 },
  { id: "TN38EF9012", type: "Reefer",      capacity: "1,500 kg", status: "Available",  driver: "Arun M.",   health: 95 },
  { id: "KA-RT-8011", type: "Heavy Duty",  capacity: "8,000 kg", status: "Maintenance",driver: "—",         health: 62 },
  { id: "MH12AB3456", type: "Dry Van",     capacity: "2,500 kg", status: "Available",  driver: "Kiran S.",  health: 100 },
  { id: "TN45GH7890", type: "Flatbed",     capacity: "4,000 kg", status: "In Transit", driver: "Priya R.",  route: "Bangalore → Pune", health: 87 },
];

const STATUS_CONFIG = {
  Available:   { color: "var(--color-emerald)", icon: ShieldCheck, label: "Available" },
  "In Transit":{ color: "var(--color-blue)",    icon: Truck,       label: "In Transit" },
  Maintenance: { color: "var(--color-amber)",   icon: AlertTriangle,label: "Maintenance" },
};

const HealthBar = ({ value }: { value: number }) => {
  const color = value >= 90 ? "var(--color-emerald)" : value >= 70 ? "var(--color-amber)" : "var(--color-rose)";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: "var(--color-border)" }}>
        <motion.div
          initial={{ width: 0 }} animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="h-full rounded-full" style={{ background: color }}
        />
      </div>
      <span className="text-[11px] font-semibold w-8 text-right" style={{ color }}>{value}%</span>
    </div>
  );
};

export const Fleet = () => {
  const available = FLEET.filter(v => v.status === "Available").length;
  const inTransit = FLEET.filter(v => v.status === "In Transit").length;
  const maintenance = FLEET.filter(v => v.status === "Maintenance").length;

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Fleet Management</p>
        <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Vehicle Registry</h1>
        <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
          Live status, health diagnostics, and driver assignments across your fleet.
        </p>
      </motion.div>

      {/* Summary Pills */}
      <motion.div
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.06, duration: 0.35 }}
        className="flex flex-wrap gap-3"
      >
        {[
          { label: "Available",   count: available,   color: "var(--color-emerald)" },
          { label: "In Transit",  count: inTransit,   color: "var(--color-blue)" },
          { label: "Maintenance", count: maintenance, color: "var(--color-amber)" },
          { label: "Total",       count: FLEET.length,color: "var(--color-text-2)" },
        ].map(({ label, count, color }) => (
          <div key={label} className="flex items-center gap-2 px-4 py-2 rounded-xl text-[12px] font-semibold"
            style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)", color }}>
            <span className="text-lg font-black">{count}</span>
            <span style={{ color: "var(--color-text-3)" }}>{label}</span>
          </div>
        ))}
      </motion.div>

      {/* Vehicle Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {FLEET.map((v, i) => {
          const cfg = STATUS_CONFIG[v.status];
          const StatusIcon = cfg.icon;
          return (
            <motion.div
              key={v.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 + i * 0.06, duration: 0.38, ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -3, transition: { duration: 0.2 } }}
              className="grad-border rounded-2xl p-5 flex flex-col gap-4 cursor-pointer group relative overflow-hidden"
              style={{ background: "var(--color-surface-1)" }}
            >
              {/* Ambient glow on hover */}
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                style={{ background: `radial-gradient(circle at 50% 0%, ${cfg.color}08 0%, transparent 60%)` }} />

              {/* Top row */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                    style={{ background: `${cfg.color}15`, border: `1px solid ${cfg.color}25` }}>
                    <Truck className="w-4.5 h-4.5" style={{ color: cfg.color }} />
                  </div>
                  <div>
                    <p className="text-[13px] font-bold font-mono" style={{ color: "var(--color-text-1)" }}>{v.id}</p>
                    <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>{v.type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold"
                  style={{ background: `${cfg.color}12`, border: `1px solid ${cfg.color}22`, color: cfg.color }}>
                  <StatusIcon className="w-3 h-3" />
                  {cfg.label}
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2">
                  <Weight className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--color-text-3)" }} />
                  <div>
                    <p className="text-[10px]" style={{ color: "var(--color-text-3)" }}>Capacity</p>
                    <p className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>{v.capacity}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <User className="w-3.5 h-3.5 shrink-0" style={{ color: "var(--color-text-3)" }} />
                  <div>
                    <p className="text-[10px]" style={{ color: "var(--color-text-3)" }}>Driver</p>
                    <p className="text-[12px] font-semibold" style={{ color: "var(--color-text-1)" }}>{v.driver}</p>
                  </div>
                </div>
              </div>

              {v.route && (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg"
                  style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                  <MapPin className="w-3 h-3 shrink-0" style={{ color: "var(--color-blue)" }} />
                  <span className="text-[11px] font-medium" style={{ color: "var(--color-text-2)" }}>{v.route}</span>
                </div>
              )}

              {/* Health bar */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-3)" }}>
                    Vehicle Health
                  </span>
                  {v.status === "Maintenance" && (
                    <span className="flex items-center gap-1 text-[10px] font-semibold" style={{ color: "var(--color-amber)" }}>
                      <Wrench className="w-3 h-3" /> Service needed
                    </span>
                  )}
                </div>
                <HealthBar value={v.health} />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

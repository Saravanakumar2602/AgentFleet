import { useEffect } from "react";
import { motion } from "framer-motion";
import { Truck, ShieldCheck, Wrench, AlertTriangle, Weight, User, RefreshCw } from "lucide-react";
import { useFleet } from "../../hooks/useFleet";
import { useToast } from "../../context/ToastContext";
import { SkeletonVehicleCard } from "../../components/ui/Skeleton";

const STATUS_CONFIG = {
  Available:   { color: "var(--color-emerald)", icon: ShieldCheck,   label: "Available" },
  Busy:        { color: "var(--color-blue)",    icon: Truck,         label: "In Transit" },
  Maintenance: { color: "var(--color-amber)",   icon: AlertTriangle, label: "Maintenance" },
} as const;

const HealthBar = ({ value }: { value: number }) => {
  const color = value >= 90 ? "var(--color-emerald)" : value >= 70 ? "var(--color-amber)" : "var(--color-rose)";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: "var(--color-border)" }}>
        <motion.div
          initial={{ width: 0 }} animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
          className="h-full rounded-full" style={{ background: color }}
        />
      </div>
      <span className="text-[11px] font-semibold w-8 text-right" style={{ color }}>{value}%</span>
    </div>
  );
};

export const Fleet = () => {
  const { vehicles, isLoading, isError, refetch } = useFleet();
  const { toast } = useToast();

  useEffect(() => {
    if (isError) {
      toast("error", "Could not load vehicle health data from backend.", refetch);
    }
  }, [isError, toast, refetch]);

  // Derive summary counts from live data
  const available   = vehicles.filter(v => v.health?.vehicle_status === "Healthy" || (!v.health && !v.isError)).length;
  const maintenance = vehicles.filter(v => v.health?.vehicle_status === "Maintenance Required").length;
  const inTransit   = vehicles.length - available - maintenance;

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
        <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--color-blue)" }}>Fleet Management</p>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-[26px] font-black tracking-tight" style={{ color: "var(--color-text-1)" }}>Vehicle Registry</h1>
            <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-2)" }}>
              Live status, health diagnostics, and driver assignments across your fleet.
            </p>
          </div>
          <button
            onClick={refetch}
            aria-label="Refresh fleet data"
            className="flex items-center gap-2 px-3 py-2 rounded-xl text-[12px] font-medium transition-colors cursor-pointer shrink-0 mt-1"
            style={{ background: "var(--color-surface-1)", border: "1px solid var(--color-border)", color: "var(--color-text-2)" }}
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </motion.div>

      {/* Summary Pills */}
      <motion.div
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.06, duration: 0.35 }}
        className="flex flex-wrap gap-3"
      >
        {[
          { label: "Healthy",     count: available,   color: "var(--color-emerald)" },
          { label: "In Transit",  count: inTransit,   color: "var(--color-blue)" },
          { label: "Maintenance", count: maintenance, color: "var(--color-amber)" },
          { label: "Total",       count: vehicles.length, color: "var(--color-text-2)" },
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
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <SkeletonVehicleCard key={i} />)
          : vehicles.map((v, i) => {
              // Derive status from live health data
              const rawStatus = v.health?.vehicle_status;
              const status: keyof typeof STATUS_CONFIG =
                rawStatus === "Maintenance Required" ? "Maintenance"
                : rawStatus === "Service Recommended" ? "Busy"
                : "Available";

              const cfg = STATUS_CONFIG[status];
              const StatusIcon = cfg.icon;
              const healthScore = v.health?.health_score ?? 100;

              return (
                <motion.div
                  key={v.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.08 + i * 0.06, duration: 0.38, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
                  whileHover={{ y: -3, transition: { duration: 0.2 } }}
                  className="grad-border rounded-2xl p-5 flex flex-col gap-4 cursor-pointer group relative overflow-hidden"
                  style={{ background: "var(--color-surface-1)" }}
                >
                  {/* Ambient glow */}
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
                        <p className="text-[13px] font-bold font-mono" style={{ color: "var(--color-text-1)" }}>{v.number}</p>
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

                  {/* Live maintenance detail */}
                  {v.health?.next_service_after_km !== undefined && (
                    <div className="flex items-center gap-2 px-3 py-2 rounded-lg"
                      style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                      <Wrench className="w-3 h-3 shrink-0" style={{ color: "var(--color-amber)" }} />
                      <span className="text-[11px] font-medium" style={{ color: "var(--color-text-2)" }}>
                        Next service in {v.health.next_service_after_km} km
                      </span>
                    </div>
                  )}

                  {/* Health bar — live from backend */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--color-text-3)" }}>
                        Vehicle Health
                      </span>
                      {v.isError && (
                        <span className="text-[10px] font-semibold" style={{ color: "var(--color-rose)" }}>
                          API error
                        </span>
                      )}
                    </div>
                    <HealthBar value={healthScore} />
                  </div>
                </motion.div>
              );
            })
        }
      </div>
    </div>
  );
};

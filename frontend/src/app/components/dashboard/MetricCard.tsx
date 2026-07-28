import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { cn } from "../../lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon: LucideIcon;
  description?: string;
  color?: string;
}

export const MetricCard = ({
  title,
  value,
  change,
  changeType = "neutral",
  icon: Icon,
  description,
  color = "text-primary",
}: MetricCardProps) => {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className="bg-card-dark border border-border-dark p-6 rounded-xl shadow-sm hover:border-text-muted/20 hover:shadow-lg transition-colors glass-glow select-none"
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted">
          {title}
        </span>
        <div className={cn("p-2 rounded-lg bg-bg-dark border border-border-dark/60", color)}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-3.5 flex items-baseline space-x-2.5">
        <span className="text-2xl font-extrabold tracking-tight text-text-main">
          {value}
        </span>
        {change && (
          <span
            className={cn(
              "text-[10px] font-bold px-2 py-0.5 rounded-full border",
              changeType === "positive" && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
              changeType === "negative" && "bg-red-500/10 text-red-400 border-red-500/20",
              changeType === "neutral" && "bg-text-muted/10 text-text-muted border-border-dark"
            )}
          >
            {change}
          </span>
        )}
      </div>

      {description && (
        <p className="mt-2 text-xs text-text-muted/80 leading-relaxed font-medium">
          {description}
        </p>
      )}
    </motion.div>
  );
};

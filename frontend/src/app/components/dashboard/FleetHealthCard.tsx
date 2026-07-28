import { ShieldCheck, AlertCircle } from "lucide-react";

interface FleetHealthCardProps {
  score: number;
}

export const FleetHealthCard = ({ score }: FleetHealthCardProps) => {
  // SVG Circle stroke parameters
  const radius = 56;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-card-dark border border-border-dark p-6 rounded-xl shadow-sm glass-glow flex flex-col justify-between h-full min-h-[220px]">
      <div>
        <h3 className="text-xs uppercase font-extrabold tracking-wider text-text-muted">
          Fleet Health Rating
        </h3>
        <p className="text-[10px] text-text-muted/60 mt-0.5">Real-time status overview</p>
      </div>

      <div className="flex items-center justify-between my-2">
        {/* Radial Progress Circle */}
        <div className="relative flex items-center justify-center shrink-0">
          <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
            {/* Background Circle */}
            <circle
              stroke="#27272A"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            {/* Foreground Radial */}
            <circle
              stroke="url(#health-gradient)"
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + " " + circumference}
              style={{ strokeDashoffset }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            {/* Defs Gradient Definitions */}
            <defs>
              <linearGradient id="health-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#6366F1" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-2xl font-black text-text-main leading-none">{score}%</span>
            <span className="text-[9px] uppercase tracking-wider text-text-muted mt-1 font-bold">Optimal</span>
          </div>
        </div>

        {/* Right Legend status indicators */}
        <div className="space-y-3.5 pl-6 flex-1">
          <div className="flex items-start space-x-2.5 text-xs text-text-muted">
            <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-text-main block">Active Fleet</span>
              <span className="text-[10px] text-text-muted/80">9 Vehicles operational</span>
            </div>
          </div>

          <div className="flex items-start space-x-2.5 text-xs text-text-muted">
            <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-text-main block">Service Tasks</span>
              <span className="text-[10px] text-text-muted/80">1 Recommended task</span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-[10px] text-text-muted/80 font-medium leading-relaxed pt-2 border-t border-border-dark/60">
        All diagnostic endpoints operating normally. Zero critical alerts reported.
      </div>
    </div>
  );
};

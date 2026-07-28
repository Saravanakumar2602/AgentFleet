import { Terminal, Clock, Activity } from "lucide-react";

interface RequestLog {
  timestamp: string;
  query: string;
  intent: string;
  latencyMs: number;
}

const RECENT_REQUESTS: RequestLog[] = [
  {
    timestamp: "10:14:22 AM",
    query: "Deliver 2.5 tons Chennai to Coimbatore",
    intent: "fleet_delivery",
    latencyMs: 142,
  },
  {
    timestamp: "10:11:05 AM",
    query: "Check diagnostic status of TN38AB1234",
    intent: "maintenance_check",
    latencyMs: 98,
  },
  {
    timestamp: "09:44:18 AM",
    query: "Get fleet optimization reports today",
    intent: "analytics_report",
    latencyMs: 215,
  },
];

export const AIRequestsCard = () => {
  return (
    <div className="bg-card-dark border border-border-dark p-6 rounded-xl shadow-sm glass-glow flex flex-col h-full min-h-[300px]">
      <div className="flex items-center justify-between pb-3.5 border-b border-border-dark/60">
        <div>
          <h3 className="text-xs uppercase font-extrabold tracking-wider text-text-muted">
            AI Orchestration Logger
          </h3>
          <p className="text-[10px] text-text-muted/60 mt-0.5">Conversational intent extractions</p>
        </div>
        <span className="px-2.5 py-1 bg-accent/10 border border-accent/20 text-accent rounded-lg font-bold text-[10px] uppercase tracking-wider flex items-center gap-1">
          <Activity className="w-3 h-3 animate-pulse" />
          Active
        </span>
      </div>

      <div className="flex-1 py-4 space-y-4 overflow-y-auto">
        {RECENT_REQUESTS.map((req, idx) => (
          <div key={idx} className="bg-bg-dark/40 border border-border-dark p-3 rounded-lg flex flex-col space-y-2 hover:border-border-dark/95 transition-all">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-text-muted/80 font-medium flex items-center gap-1">
                <Terminal className="w-3 h-3 text-primary" />
                {req.timestamp}
              </span>
              <span className="font-semibold text-text-muted">{req.intent}</span>
            </div>
            
            <p className="text-xs text-text-main font-semibold tracking-wide truncate">
              "{req.query}"
            </p>

            <div className="flex items-center text-[10px] text-text-muted/80 font-bold bg-bg-dark border border-border-dark/50 rounded-md px-2 py-0.5 w-max">
              <Clock className="w-3 h-3 mr-1 text-amber-500" />
              Latency: {req.latencyMs}ms
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

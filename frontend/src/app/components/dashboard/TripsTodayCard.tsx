import { MapPin, Navigation, Compass, ArrowRight } from "lucide-react";

interface TripData {
  id: string;
  driver: string;
  vehicle: string;
  source: string;
  destination: string;
  progress: number;
  status: "In Transit" | "Completed" | "Pending";
}

const ACTIVE_TRIPS: TripData[] = [
  {
    id: "TRIP-001",
    driver: "Ravi K.",
    vehicle: "TN38AB1234",
    source: "Chennai",
    destination: "Coimbatore",
    progress: 68,
    status: "In Transit",
  },
  {
    id: "TRIP-002",
    driver: "Suresh P.",
    vehicle: "KA-RT-8011",
    source: "Bangalore",
    destination: "Chennai",
    progress: 15,
    status: "In Transit",
  },
  {
    id: "TRIP-003",
    driver: "Arun M.",
    vehicle: "TN38EF9012",
    source: "Mumbai",
    destination: "Pune",
    progress: 100,
    status: "Completed",
  },
];

export const TripsTodayCard = () => {
  return (
    <div className="bg-card-dark border border-border-dark p-6 rounded-xl shadow-sm glass-glow flex flex-col h-full min-h-[300px]">
      <div className="flex items-center justify-between pb-3.5 border-b border-border-dark/60">
        <div>
          <h3 className="text-xs uppercase font-extrabold tracking-wider text-text-muted">
            Live Deliveries Tracker
          </h3>
          <p className="text-[10px] text-text-muted/60 mt-0.5">Active trips in progress</p>
        </div>
        <span className="px-2.5 py-1 bg-primary/10 border border-primary/20 text-primary rounded-lg font-bold text-[10px] uppercase tracking-wider">
          Active: 2
        </span>
      </div>

      <div className="flex-1 py-4 space-y-5 overflow-y-auto">
        {ACTIVE_TRIPS.map((trip) => {
          const isInTransit = trip.status === "In Transit";
          const isCompleted = trip.status === "Completed";

          return (
            <div key={trip.id} className="space-y-3">
              {/* Trip Header Metadata */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2.5">
                  <span className="font-extrabold text-text-main text-[11px]">{trip.id}</span>
                  <span className="text-[10px] text-text-muted/70">{trip.vehicle}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] text-text-muted font-medium">{trip.driver}</span>
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isCompleted ? "bg-emerald-500" : "bg-primary animate-pulse"
                    }`}
                  />
                </div>
              </div>

              {/* Source -> Destination Visual Line */}
              <div className="flex items-center space-x-3.5 text-xs">
                <div className="flex items-center space-x-1.5 text-text-main font-semibold">
                  <MapPin className="w-3.5 h-3.5 text-primary shrink-0" />
                  <span className="truncate max-w-[80px]">{trip.source}</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-text-muted/40 shrink-0" />
                <div className="flex items-center space-x-1.5 text-text-main font-semibold">
                  <Navigation className="w-3.5 h-3.5 text-accent shrink-0" />
                  <span className="truncate max-w-[80px]">{trip.destination}</span>
                </div>
                {isInTransit && (
                  <span className="text-[10px] text-text-muted ml-auto font-medium flex items-center gap-1">
                    <Compass className="w-3 h-3 text-text-muted animate-spin-slow" />
                    {trip.progress}%
                  </span>
                )}
              </div>

              {/* Progress Line Bar */}
              <div className="w-full bg-border-dark/60 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isCompleted ? "bg-emerald-500" : "bg-gradient-to-r from-primary to-accent"
                  }`}
                  style={{ width: `${trip.progress}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

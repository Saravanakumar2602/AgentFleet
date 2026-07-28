import { cn } from "../../lib/utils";

interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
}

export const Skeleton = ({ className, style }: SkeletonProps) => (
  <div
    className={cn("rounded-lg shimmer", className)}
    style={{ background: "var(--color-surface-2)", ...style }}
    aria-hidden="true"
  />
);

export const SkeletonCard = ({ rows = 3 }: { rows?: number }) => (
  <div
    className="grad-border rounded-2xl p-5 flex flex-col gap-4"
    style={{ background: "var(--color-surface-1)" }}
    aria-busy="true"
    aria-label="Loading"
  >
    <div className="flex items-center justify-between">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-7 w-7 rounded-lg" />
    </div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex items-center justify-between py-1.5">
        <Skeleton className="h-2.5" style={{ width: `${40 + i * 12}%` }} />
        <Skeleton className="h-2.5 w-16" />
      </div>
    ))}
  </div>
);

export const SkeletonVehicleCard = () => (
  <div
    className="grad-border rounded-2xl p-5 flex flex-col gap-4"
    style={{ background: "var(--color-surface-1)" }}
    aria-busy="true"
    aria-label="Loading vehicle"
  >
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-3">
        <Skeleton className="w-9 h-9 rounded-xl" />
        <div className="flex flex-col gap-1.5">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-2.5 w-16" />
        </div>
      </div>
      <Skeleton className="h-6 w-20 rounded-lg" />
    </div>
    <div className="grid grid-cols-2 gap-3">
      <Skeleton className="h-10 rounded-lg" />
      <Skeleton className="h-10 rounded-lg" />
    </div>
    <div className="flex flex-col gap-1.5">
      <Skeleton className="h-2.5 w-24" />
      <Skeleton className="h-1.5 w-full rounded-full" />
    </div>
  </div>
);

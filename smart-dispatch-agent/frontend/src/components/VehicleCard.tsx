import { Truck } from "lucide-react";

interface VehicleCardProps {
  vehicleNumber: string;
  capacity: number;
  status: "Available" | "Busy";
}

export const VehicleCard = ({
  vehicleNumber,
  capacity,
  status,
}: VehicleCardProps) => {
  const isAvailable = status === "Available";

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex items-center justify-between hover:border-blue-100 hover:shadow-md transition-all duration-200">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${isAvailable ? 'bg-blue-50 text-blue-600' : 'bg-slate-100 text-slate-500'}`}>
          <Truck className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-semibold text-slate-800 text-sm">{vehicleNumber}</h4>
          <p className="text-xs text-slate-500">Cap: {capacity} kg</p>
        </div>
      </div>
      <div>
        <span
          className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
            isAvailable
              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
              : "bg-amber-50 text-amber-700 border border-amber-200"
          }`}
        >
          {status}
        </span>
      </div>
    </div>
  );
};

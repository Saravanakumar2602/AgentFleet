import { CheckCircle2, AlertCircle, ShieldCheck, MapPin, Navigation, Clock, Truck, User } from "lucide-react";
import type { DispatchResponse } from "../services/api";

interface ResultCardProps {
  result: DispatchResponse;
}

export const ResultCard = ({ result }: ResultCardProps) => {
  const isSuccess = result.status === "success";

  if (!isSuccess) {
    return (
      <div className="bg-red-50 p-6 rounded-2xl border border-red-200 shadow-sm flex items-start space-x-4 animate-success-pop">
        <div className="p-3 bg-red-100 text-red-600 rounded-xl">
          <AlertCircle className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="text-red-800 font-bold text-lg">No Suitable Vehicle Available</h3>
          <p className="text-sm text-red-600 font-semibold">{result.message}</p>
          <p className="text-xs text-red-500/80 pt-1">
            Check the cargo weight limit or wait until active trucks return to Available state.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-emerald-50/50 p-6 rounded-2xl border border-emerald-200 shadow-sm animate-success-pop space-y-6">
      {/* Header Banner */}
      <div className="flex items-center justify-between pb-4 border-b border-emerald-100">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-emerald-100 text-emerald-600 rounded-xl">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-emerald-800 font-extrabold text-lg flex items-center gap-1.5">
              ✅ Vehicle Assigned
            </h3>
            <p className="text-xs text-emerald-600/90 font-semibold">Orchestration matched successfully</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold text-xs uppercase tracking-wider border border-emerald-200">
          Matched
        </span>
      </div>

      {/* Grid Specs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Column: Vehicle & Driver details */}
        <div className="space-y-3">
          <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs flex items-center space-x-3">
            <Truck className="w-5 h-5 text-emerald-600" />
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Assigned Vehicle</p>
              <h4 className="font-bold text-slate-800 text-sm">{result.vehicle_number}</h4>
              <p className="text-xs text-slate-500">Max Capacity: {result.capacity} kg</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs flex items-center space-x-3">
            <User className="w-5 h-5 text-indigo-600" />
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Driver Allocated</p>
              <h4 className="font-bold text-slate-800 text-sm">{result.driver}</h4>
              <p className="text-xs text-slate-500">Active Operator</p>
            </div>
          </div>
        </div>

        {/* Right Column: Route Details */}
        <div className="space-y-3">
          <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs flex items-center space-x-3">
            <MapPin className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Pickup Point</p>
              <h4 className="font-bold text-slate-800 text-sm">{result.pickup}</h4>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs flex items-center space-x-3">
            <Navigation className="w-5 h-5 text-indigo-500" />
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Destination Delivery</p>
              <h4 className="font-bold text-slate-800 text-sm">{result.destination}</h4>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Timing */}
      <div className="bg-white/80 p-4 rounded-xl border border-emerald-100 flex items-center justify-between">
        <div className="flex items-center space-x-2.5 text-slate-700">
          <Clock className="w-5 h-5 text-amber-500" />
          <div>
            <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Estimated Travel Duration</p>
            <h4 className="font-bold text-slate-800 text-sm">{result.estimated_time}</h4>
          </div>
        </div>
        <div className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-100/40 px-3 py-1.5 rounded-lg border border-emerald-100">
          <ShieldCheck className="w-4 h-4 mr-1 text-emerald-600" />
          Secure Dispatch
        </div>
      </div>
    </div>
  );
};

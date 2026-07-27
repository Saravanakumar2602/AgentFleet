import { User } from "lucide-react";

interface DriverCardProps {
  name: string;
  status: "Available" | "Busy";
}

export const DriverCard = ({ name, status }: DriverCardProps) => {
  const isAvailable = status === "Available";

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex items-center justify-between hover:border-blue-100 hover:shadow-md transition-all duration-200">
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${isAvailable ? 'bg-indigo-50 text-indigo-600' : 'bg-slate-100 text-slate-500'}`}>
          <User className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-semibold text-slate-800 text-sm">{name}</h4>
          <p className="text-xs text-slate-500">Driver Profile</p>
        </div>
      </div>
      <div>
        <span
          className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
            isAvailable
              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
              : "bg-slate-100 text-slate-600 border border-slate-200"
          }`}
        >
          {status}
        </span>
      </div>
    </div>
  );
};

import { useForm } from "react-hook-form";
import { MapPin, Navigation, Weight, Play } from "lucide-react";

export interface DispatchFormData {
  pickup: string;
  destination: string;
  weight: number;
}

interface DispatchFormProps {
  onSubmit: (data: DispatchFormData) => void;
  isLoading: boolean;
}

export const DispatchForm = ({ onSubmit, isLoading }: DispatchFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<DispatchFormData>({
    defaultValues: {
      pickup: "",
      destination: "",
      weight: undefined,
    },
  });

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 space-y-6"
    >
      <div>
        <h3 className="text-lg font-bold text-slate-800">Dispatch Order Input</h3>
        <p className="text-xs text-slate-500">Provide pickup and delivery details to assign route vehicles</p>
      </div>

      <div className="space-y-4">
        {/* Pickup Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
            Pickup Point
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <MapPin className="w-4 h-4 text-blue-500" />
            </span>
            <input
              type="text"
              placeholder="e.g. Chennai"
              className={`w-full pl-10 pr-4 py-2.5 rounded-xl border ${
                errors.pickup ? "border-red-300 focus:ring-red-100" : "border-slate-200 focus:ring-blue-100"
              } focus:border-blue-500 focus:ring-4 focus:outline-none transition-all text-sm`}
              {...register("pickup", { required: "Pickup point is required" })}
            />
          </div>
          {errors.pickup && (
            <p className="text-xs text-red-500 mt-1 font-semibold">{errors.pickup.message}</p>
          )}
        </div>

        {/* Destination Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
            Destination Point
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <Navigation className="w-4 h-4 text-indigo-500" />
            </span>
            <input
              type="text"
              placeholder="e.g. Coimbatore"
              className={`w-full pl-10 pr-4 py-2.5 rounded-xl border ${
                errors.destination ? "border-red-300 focus:ring-red-100" : "border-slate-200 focus:ring-blue-100"
              } focus:border-blue-500 focus:ring-4 focus:outline-none transition-all text-sm`}
              {...register("destination", { required: "Destination point is required" })}
            />
          </div>
          {errors.destination && (
            <p className="text-xs text-red-500 mt-1 font-semibold">{errors.destination.message}</p>
          )}
        </div>

        {/* Weight Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
            Cargo Weight (kg)
          </label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
              <Weight className="w-4 h-4 text-amber-500" />
            </span>
            <input
              type="number"
              placeholder="e.g. 2500"
              step="any"
              className={`w-full pl-10 pr-4 py-2.5 rounded-xl border ${
                errors.weight ? "border-red-300 focus:ring-red-100" : "border-slate-200 focus:ring-blue-100"
              } focus:border-blue-500 focus:ring-4 focus:outline-none transition-all text-sm`}
              {...register("weight", {
                required: "Cargo weight is required",
                min: { value: 0.1, message: "Weight must be greater than 0 kg" },
              })}
            />
          </div>
          {errors.weight && (
            <p className="text-xs text-red-500 mt-1 font-semibold">{errors.weight.message}</p>
          )}
        </div>
      </div>

      <div className="pt-2 flex space-x-3">
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 px-4 rounded-xl shadow-md focus:outline-none focus:ring-4 focus:ring-blue-100 transition-all flex items-center justify-center space-x-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>Matching Fleet...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Assign Vehicle</span>
            </>
          )}
        </button>
        <button
          type="button"
          onClick={() => reset()}
          disabled={isLoading}
          className="px-4 py-3 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-all text-sm font-semibold cursor-pointer"
        >
          Reset
        </button>
      </div>
    </form>
  );
};

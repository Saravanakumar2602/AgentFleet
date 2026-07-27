import { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { DispatchForm } from "../components/DispatchForm";
import type { DispatchFormData } from "../components/DispatchForm";
import { VehicleCard } from "../components/VehicleCard";
import { DriverCard } from "../components/DriverCard";
import { ResultCard } from "../components/ResultCard";
import { dispatchApi } from "../services/api";
import type { DispatchResponse, FleetStatusResponse } from "../services/api";
import { Truck, Users, RefreshCw } from "lucide-react";

export const Home = () => {
  const [fleet, setFleet] = useState<FleetStatusResponse | null>(null);
  const [dispatchResult, setDispatchResult] = useState<DispatchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchFleetStatus = async () => {
    try {
      const data = await dispatchApi.getFleetStatus();
      setFleet(data);
    } catch (err) {
      console.error("Failed to load fleet status:", err);
    }
  };

  useEffect(() => {
    fetchFleetStatus();
  }, []);

  const handleDispatchSubmit = async (formData: DispatchFormData) => {
    setIsLoading(true);
    setDispatchResult(null);

    // Simulate 2-second loading animation requested
    setTimeout(async () => {
      try {
        const response = await dispatchApi.assignDispatch(
          formData.pickup,
          formData.destination,
          formData.weight
        );
        setDispatchResult(response);
        // Refresh fleet list status dynamically
        fetchFleetStatus();
      } catch (err: any) {
        setDispatchResult({
          status: "failed",
          message: err.response?.data?.message || "Internal connection error to dispatcher API.",
        });
      } finally {
        setIsLoading(false);
      }
    }, 2000);
  };

  const handleRefreshClick = async () => {
    setRefreshing(true);
    await fetchFleetStatus();
    setTimeout(() => setRefreshing(false), 500);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navbar */}
      <Navbar />

      {/* Main Container Dashboard */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        
        {/* Left Side Column: Dispatch Form & Assignment Result */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Dispatch Input Form */}
          <DispatchForm onSubmit={handleDispatchSubmit} isLoading={isLoading} />

          {/* Loading Placeholder */}
          {isLoading && (
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col items-center justify-center space-y-3 py-10 animate-pulse-slow">
              <span className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></span>
              <p className="text-sm font-semibold text-slate-600">Selecting Best Matching Driver & Vehicle...</p>
            </div>
          )}

          {/* Result Card Placement */}
          {dispatchResult && !isLoading && (
            <ResultCard result={dispatchResult} />
          )}

        </div>

        {/* Right Side Column: Fleet Status Sidebar */}
        <div className="space-y-6 lg:col-span-1">
          
          <div className="bg-slate-100/50 p-6 rounded-2xl border border-slate-200/60 space-y-6">
            
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                  Live Fleet Status
                </h3>
                <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Operational Monitor</p>
              </div>
              <button
                onClick={handleRefreshClick}
                disabled={refreshing}
                className="p-2 bg-white rounded-lg border border-slate-200 hover:bg-slate-50 hover:shadow-xs transition-all text-slate-500 cursor-pointer disabled:opacity-40"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {/* Vehicles Sub-List */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Truck className="w-4 h-4 text-blue-600" />
                Vehicles Fleet
              </h4>
              <div className="space-y-2.5">
                {fleet?.vehicles.map((v) => (
                  <VehicleCard
                    key={v.vehicle_number}
                    vehicleNumber={v.vehicle_number}
                    capacity={v.capacity}
                    status={v.status}
                  />
                ))}
                {!fleet && (
                  <div className="text-xs text-slate-400 py-2">Loading vehicles...</div>
                )}
              </div>
            </div>

            {/* Drivers Sub-List */}
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-indigo-600" />
                Allocated Drivers
              </h4>
              <div className="space-y-2.5">
                {fleet?.drivers.map((d) => (
                  <DriverCard key={d.name} name={d.name} status={d.status} />
                ))}
                {!fleet && (
                  <div className="text-xs text-slate-400 py-2">Loading drivers...</div>
                )}
              </div>
            </div>

          </div>

        </div>

      </main>

      {/* Footer Info */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        &copy; {new Date().getFullYear()} Standalone Smart Dispatch Agent Demo Platform. Built with React + FastAPI.
      </footer>
    </div>
  );
};

// ── Base API envelope ──────────────────────────────────────────────────────
export interface ApiSuccess<T = Record<string, unknown>> {
  status: "success";
  message: string;
  data?: T;
}

export interface ApiFailure {
  status: "failed";
  message: string;
  error_details?: unknown;
  errors?: { field: string; issue: string }[];
}

// ── Health ─────────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  database?: string;
  environment?: string;
  message?: string;
}

// ── Vehicles (from DB schema) ──────────────────────────────────────────────
export interface Vehicle {
  id: string;
  vehicle_number: string;
  vehicle_type: string;
  capacity_kg: number;
  fuel_type: string;
  fuel_level: number;
  status: "Available" | "Busy" | "Maintenance";
  health_score: number;
  current_driver_id: string | null;
}

// ── Dispatch ───────────────────────────────────────────────────────────────
export interface DispatchRequest {
  pickup: string;
  destination: string;
  weight: number;
}

export interface DispatchResult {
  status: string;
  message: string;
  agent: string;
  trip_id: string;
  vehicle: { id: string; vehicle_number: string };
  driver: { id: string; name: string };
}

// ── Route ──────────────────────────────────────────────────────────────────
export interface RouteResult {
  status: string;
  message: string;
  agent: string;
  trip_id: string;
  distance_km: number;
  estimated_duration: string;
  estimated_fuel: number;
}

// ── Maintenance ────────────────────────────────────────────────────────────
export interface MaintenanceResult {
  status: string;
  message: string;
  agent: string;
  vehicle_id: string;
  health_score: number;
  vehicle_status: "Healthy" | "Service Recommended" | "Maintenance Required";
  next_service_after_km?: number;
}

// ── Analytics ─────────────────────────────────────────────────────────────
export interface AnalyticsResult {
  status: string;
  message: string;
  agent: string;
  vehicle: string;
  total_trips: number;
  average_distance: number;
  fuel_efficiency: number;
  maintenance_count: number;
  utilization: number;
  recommendation: string;
}

export interface CargoValidationResult {
  cargo_weight_kg: number;
  cargo_class: string;
  is_hazardous: boolean;
  compliance_status: string;
  violations: string[];
}

export interface TrafficResult {
  traffic_level: string;
  delay_minutes: number;
  congestion_factor: number;
  recommended_departure: string;
}

export interface WeatherResult {
  location: string;
  condition: string;
  temperature_c: number;
  wind_kmh: number;
  weather_risk: string;
  risk_reasons: string[];
}

export interface EtaUpdaterResult {
  base_duration_minutes: number;
  traffic_delay_minutes: number;
  weather_delay_minutes: number;
  total_delay_minutes: number;
  original_eta: string;
  adjusted_eta: string;
}

export interface ComplianceResult {
  driver_hours_this_week: number;
  compliance_status: string;
  violations: string[];
}

export interface FuelResult {
  current_fuel_level_pct: number;
  fuel_needed_liters: number;
  estimated_fuel_cost_inr: number;
  refuel_stop_needed: boolean;
}

export interface DriverRatingResult {
  driver_score: number;
  performance_grade: string;
  feedback: string;
}

export interface InvoiceResult {
  invoice_number: string;
  distance_charge_inr: number;
  fuel_cost_inr: number;
  subtotal_inr: number;
  gst_inr: number;
  total_amount_inr: number;
}

export interface FleetSummaryResult {
  total_vehicles: number;
  active_trips: number;
  fleet_utilization_pct: number;
  avg_fleet_health_score: number;
}

export interface SosAlertResult {
  alert_triggered: boolean;
  severity: string;
  alert_types: string[];
}

// ── Supervisor ─────────────────────────────────────────────────────────────
export interface WorkflowResults {
  dispatch: {
    trip_id: string;
    vehicle: { id: string; vehicle_number: string };
    driver: { id: string; name: string };
  };
  route: {
    distance_km: number;
    estimated_duration: string;
    estimated_fuel: number;
  };
  maintenance: {
    health_score: number;
    vehicle_status: string;
    next_service_after_km?: number;
  };
  analytics: {
    utilization: number;
    recommendation: string;
  };
  customer: {
    customer_message: string;
  };
  cargo_validation?: CargoValidationResult;
  traffic?: TrafficResult;
  weather?: WeatherResult;
  eta_updater?: EtaUpdaterResult;
  compliance?: ComplianceResult;
  fuel?: FuelResult;
  driver_rating?: DriverRatingResult;
  invoice?: InvoiceResult;
  fleet_summary?: FleetSummaryResult;
  sos_alert?: SosAlertResult;
}

export interface SupervisorExecuteRequest {
  workflow: string;
  pickup: string;
  destination: string;
  weight: number;
}

export interface SupervisorExecuteResult {
  status: string;
  workflow: string;
  execution_time_ms: number;
  results: WorkflowResults;
}

export interface SupervisorChatRequest {
  message: string;
}

export interface SupervisorChatResult {
  status: string;
  intent: string;
  workflow: string;
  llm_latency_ms: number;
  total_execution_time_ms: number;
  results: WorkflowResults;
}

// ── Dashboard aggregated (computed on frontend) ────────────────────────────
export interface DashboardStats {
  systemOnline: boolean;
  dbConnected: boolean;
}

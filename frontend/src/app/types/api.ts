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

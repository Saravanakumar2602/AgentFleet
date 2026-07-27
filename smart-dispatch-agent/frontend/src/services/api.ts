import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface DispatchResponse {
  status: "success" | "failed";
  vehicle_number?: string;
  capacity?: number;
  driver?: string;
  pickup?: string;
  destination?: string;
  estimated_time?: string;
  message: string;
}

export interface FleetStatusResponse {
  vehicles: Array<{
    vehicle_number: string;
    capacity: number;
    status: "Available" | "Busy";
  }>;
  drivers: Array<{
    name: string;
    status: "Available" | "Busy";
  }>;
}

export const dispatchApi = {
  assignDispatch: async (pickup: string, destination: string, weight: number): Promise<DispatchResponse> => {
    const response = await api.post<DispatchResponse>("/dispatch", {
      pickup,
      destination,
      weight,
    });
    return response.data;
  },

  getFleetStatus: async (): Promise<FleetStatusResponse> => {
    const response = await api.get<FleetStatusResponse>("/fleet");
    return response.data;
  },
};

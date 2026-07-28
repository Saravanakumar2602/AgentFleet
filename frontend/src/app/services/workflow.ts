import { api } from "./api";
import type { SupervisorExecuteResult } from "../types/api";

export interface WorkflowTriggerPayload {
  workflow: string;
  pickup: string;
  destination: string;
  weight: number;
}

export const workflowService = {
  /** POST /supervisor/execute — trigger a named workflow */
  trigger: async (payload: WorkflowTriggerPayload): Promise<SupervisorExecuteResult> => {
    const res = await api.post<SupervisorExecuteResult>("/supervisor/execute", payload);
    return res.data;
  },
};

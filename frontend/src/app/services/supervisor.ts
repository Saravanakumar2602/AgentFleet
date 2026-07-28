import { api } from "./api";
import type {
  SupervisorChatRequest,
  SupervisorChatResult,
  SupervisorExecuteRequest,
  SupervisorExecuteResult,
} from "../types/api";

export const supervisorService = {
  /** POST /supervisor/chat — natural language → intent → workflow */
  chat: async (payload: SupervisorChatRequest): Promise<SupervisorChatResult> => {
    const res = await api.post<SupervisorChatResult>("/supervisor/chat", payload);
    return res.data;
  },

  /** POST /supervisor/execute — direct workflow trigger with explicit params */
  execute: async (payload: SupervisorExecuteRequest): Promise<SupervisorExecuteResult> => {
    const res = await api.post<SupervisorExecuteResult>("/supervisor/execute", payload);
    return res.data;
  },
};

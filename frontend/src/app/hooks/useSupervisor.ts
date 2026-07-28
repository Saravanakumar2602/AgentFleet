import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { supervisorService } from "../services/supervisor";
import type { SupervisorChatResult, WorkflowResults } from "../types/api";

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  ts: string;
  results?: WorkflowResults;
  intent?: string;
  latency?: number;
}

const ts = () =>
  new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

const uid = () => Math.random().toString(36).slice(2);

const formatAssistantContent = (data: SupervisorChatResult): string => {
  const r = data.results;
  const lines = [
    `Intent classified → ${data.intent}`,
    ``,
    `Dispatch  Vehicle ${r.dispatch.vehicle.vehicle_number} assigned to ${r.dispatch.driver.name}`,
    `Route     ${r.route.distance_km} km · ${r.route.estimated_duration} · ${r.route.estimated_fuel}L fuel`,
    `Health    ${r.maintenance.vehicle_status} (score: ${r.maintenance.health_score})`,
    `Analytics Utilization ${r.analytics.utilization}% · ${r.analytics.recommendation}`,
    `Customer  ${r.customer.customer_message}`,
    ``,
    `Completed in ${data.total_execution_time_ms}ms (LLM: ${data.llm_latency_ms}ms)`,
  ];
  return lines.join("\n");
};

export const useSupervisor = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: uid(),
      role: "assistant",
      content:
        "Hello. I'm the Fleet Supervisor Agent — powered by Llama 3.3 via Groq. I can orchestrate deliveries, check vehicle health, analyze routes, and query fleet analytics. What would you like to do?",
      ts: ts(),
    },
  ]);

  const mutation = useMutation({
    mutationFn: supervisorService.chat,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "assistant",
          content: formatAssistantContent(data),
          ts: ts(),
          results: data.results,
          intent: data.intent,
          latency: data.total_execution_time_ms,
        },
      ]);
    },
    onError: (err: Error) => {
      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "assistant",
          content: `⚠ ${err.message}`,
          ts: ts(),
        },
      ]);
    },
  });

  const sendMessage = useCallback(
    (text: string) => {
      if (!text.trim() || mutation.isPending) return;
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "user", content: text.trim(), ts: ts() },
      ]);
      mutation.mutate({ message: text.trim() });
    },
    [mutation]
  );

  return {
    messages,
    sendMessage,
    isThinking: mutation.isPending,
    error: mutation.error,
  };
};

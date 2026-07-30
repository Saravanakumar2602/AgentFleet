import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowService } from "../services/workflow";
import type { SupervisorExecuteResult, WorkflowResults } from "../types/api";

export type StepStatus = "idle" | "running" | "completed" | "failed";

export interface WorkflowStepState {
  name: string;
  role: string;
  status: StepStatus;
  detail?: string;
}

const STEP_KEYS: (keyof WorkflowResults)[] = [
  "cargo_validation",
  "dispatch",
  "traffic",
  "weather",
  "route",
  "eta_updater",
  "compliance",
  "maintenance",
  "fuel",
  "analytics",
  "driver_rating",
  "customer",
  "invoice",
  "fleet_summary",
  "sos_alert",
];

const STEP_META: { name: string; role: string }[] = [
  { name: "Cargo Validation", role: "Pre-flight Checker" },
  { name: "Dispatch Agent",    role: "Fleet Assigner" },
  { name: "Traffic Agent",     role: "Traffic Analyzer" },
  { name: "Weather Agent",     role: "Route Advisor" },
  { name: "Route Agent",       role: "Route Intelligence" },
  { name: "ETA Updater",       role: "Precision Timer" },
  { name: "Compliance Agent",  role: "Regulatory Checker" },
  { name: "Maintenance Agent", role: "Diagnostic Checker" },
  { name: "Fuel Agent",        role: "Fuel Planner" },
  { name: "Analytics Agent",   role: "Data Aggregator" },
  { name: "Driver Rating",     role: "Performance Scorer" },
  { name: "Customer Agent",    role: "Notifier Service" },
  { name: "Invoice Agent",     role: "Billing Generator" },
  { name: "Fleet Summary",     role: "Fleet KPI Reporter" },
  { name: "SOS Alert Agent",   role: "Emergency Monitor" },
];

const buildInitialSteps = (): WorkflowStepState[] =>
  STEP_META.map((m) => ({ ...m, status: "idle" }));

const STEP_DELAY_MS = 400; // slightly faster animation for 15 steps

interface WorkflowContextValue {
  steps: WorkflowStepState[];
  logs: { text: string; type: "info" | "success" | "system" | "error" }[];
  result: SupervisorExecuteResult | null;
  isDone: boolean;
  isRunning: boolean;
  isError: boolean;
  error: Error | null;
  trigger: (payload: Parameters<typeof workflowService.trigger>[0]) => void;
  reset: () => void;
}

const WorkflowContext = createContext<WorkflowContextValue | null>(null);

export const WorkflowProvider = ({ children }: { children: ReactNode }) => {
  const queryClient = useQueryClient();
  const [steps, setSteps] = useState<WorkflowStepState[]>(buildInitialSteps());
  const [logs, setLogs] = useState<{ text: string; type: "info" | "success" | "system" | "error" }[]>([]);
  const [result, setResult] = useState<SupervisorExecuteResult | null>(null);
  const [isDone, setIsDone] = useState(false);

  const reset = useCallback(() => {
    setSteps(buildInitialSteps());
    setLogs([]);
    setResult(null);
    setIsDone(false);
  }, []);

  const animateSteps = useCallback((data: SupervisorExecuteResult) => {
    setResult(data);
    setLogs([{ text: "[Supervisor] Workflow initiated. Sequencing 15 agents...", type: "info" }]);

    STEP_KEYS.forEach((key, i) => {
      // Mark running
      setTimeout(() => {
        setSteps((prev) =>
          prev.map((s, idx) => (idx === i ? { ...s, status: "running" } : s))
        );
        setLogs((prev) => [
          ...prev,
          { text: `[System] Launching ${STEP_META[i].name}...`, type: "system" },
        ]);
      }, i * STEP_DELAY_MS);

      // Mark completed
      setTimeout(() => {
        const stepData = data.results[key] as Record<string, unknown>;
        const detail = stepData
          ? Object.entries(stepData)
              .map(([k, v]) => {
                if (typeof v === "object" && v !== null) {
                  return `${k}: ${JSON.stringify(v)}`;
                }
                return `${k}: ${v}`;
              })
              .join(" · ")
          : "";

        setSteps((prev) =>
          prev.map((s, idx) => (idx === i ? { ...s, status: "completed", detail } : s))
        );
        setLogs((prev) => [
          ...prev,
          { text: `[${STEP_META[i].name}] ✓ Completed`, type: "success" },
        ]);

        if (i === STEP_KEYS.length - 1) {
          setTimeout(() => {
            setLogs((prev) => [
              ...prev,
              {
                text: `[Supervisor] All agents completed in ${data.execution_time_ms}ms. Transaction persisted.`,
                type: "info",
              },
            ]);
            setIsDone(true);
          }, 200);
        }
      }, i * STEP_DELAY_MS + STEP_DELAY_MS - 100);
    });
  }, []);

  const mutation = useMutation({
    mutationFn: workflowService.trigger,
    onMutate: () => {
      reset();
      setLogs([{ text: "[Supervisor] Connecting to backend...", type: "system" }]);
    },
    onSuccess: (data) => {
      animateSteps(data);
      queryClient.invalidateQueries({ queryKey: ["fleet"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: (err: Error) => {
      setSteps((prev) =>
        prev.map((s) => (s.status === "running" ? { ...s, status: "failed" } : s))
      );
      setLogs((prev) => [
        ...prev,
        { text: `[Error] ${err.message}`, type: "error" },
      ]);
    },
  });

  const trigger = useCallback(
    (payload: Parameters<typeof workflowService.trigger>[0]) => {
      mutation.mutate(payload);
    },
    [mutation]
  );

  return (
    <WorkflowContext.Provider value={{
      steps,
      logs,
      result,
      isDone,
      isRunning: mutation.isPending,
      isError: mutation.isError,
      error: mutation.error,
      trigger,
      reset,
    }}>
      {children}
    </WorkflowContext.Provider>
  );
};

export const useWorkflowContext = (): WorkflowContextValue => {
  const ctx = useContext(WorkflowContext);
  if (!ctx) throw new Error("useWorkflowContext must be used inside <WorkflowProvider>");
  return ctx;
};

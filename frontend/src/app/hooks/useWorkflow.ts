import { useState, useCallback } from "react";
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
  "dispatch",
  "route",
  "maintenance",
  "analytics",
  "customer",
];

const STEP_META: { name: string; role: string }[] = [
  { name: "Dispatch Agent",    role: "Fleet Assigner" },
  { name: "Route Agent",       role: "Route Intelligence" },
  { name: "Maintenance Agent", role: "Diagnostic Checker" },
  { name: "Analytics Agent",   role: "Data Aggregator" },
  { name: "Customer Agent",    role: "Notifier Service" },
];

const buildInitialSteps = (): WorkflowStepState[] =>
  STEP_META.map((m) => ({ ...m, status: "idle" }));

const STEP_DELAY_MS = 600;

export const useWorkflow = () => {
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
    setLogs([{ text: "[Supervisor] Workflow initiated. Sequencing agents...", type: "info" }]);

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
        const detail = Object.entries(stepData)
          .map(([k, v]) => `${k}: ${v}`)
          .join(" · ");

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
      // Invalidate fleet & dashboard queries to force immediate UI updates
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

  return {
    steps,
    logs,
    result,
    isDone,
    isRunning: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error,
    trigger,
    reset,
  };
};

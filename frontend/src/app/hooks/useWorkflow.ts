// Re-exports the global workflow context so existing import paths in Workflow.tsx still work.
export { useWorkflowContext as useWorkflow } from "../context/WorkflowContext";
export type { WorkflowStepState, StepStatus } from "../context/WorkflowContext";

import { StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "./app/context/ToastContext";
import { WorkflowProvider } from "./app/context/WorkflowContext";
import "./index.css";
import App from "./App.tsx";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <WorkflowProvider>
          <Suspense fallback={null}>
            <App />
          </Suspense>
        </WorkflowProvider>
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>
);

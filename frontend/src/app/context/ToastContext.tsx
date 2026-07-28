import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, AlertCircle, XCircle, X, RefreshCw } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  onRetry?: () => void;
}

interface ToastContextValue {
  toast: (type: ToastType, message: string, onRetry?: () => void) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export const useToast = () => useContext(ToastContext);

const ICONS = {
  success: CheckCircle2,
  error:   XCircle,
  info:    AlertCircle,
};

const COLORS = {
  success: { color: "var(--color-emerald)", bg: "rgba(52,211,153,0.08)", border: "rgba(52,211,153,0.2)" },
  error:   { color: "var(--color-rose)",    bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.2)" },
  info:    { color: "var(--color-blue)",    bg: "rgba(79,142,247,0.08)",  border: "rgba(79,142,247,0.2)" },
};

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((p) => p.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((type: ToastType, message: string, onRetry?: () => void) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((p) => [...p, { id, type, message, onRetry }]);
    setTimeout(() => dismiss(id), type === "error" ? 8000 : 4000);
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div
        className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none"
        aria-live="polite"
        aria-label="Notifications"
      >
        <AnimatePresence>
          {toasts.map((t) => {
            const Icon = ICONS[t.type];
            const c = COLORS[t.type];
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, y: 12, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.96 }}
                transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] }}
                className="pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl max-w-sm"
                style={{ background: c.bg, border: `1px solid ${c.border}`, backdropFilter: "blur(12px)" }}
                role="alert"
              >
                <Icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: c.color }} />
                <p className="flex-1 text-[12px] leading-relaxed" style={{ color: "var(--color-text-1)" }}>
                  {t.message}
                </p>
                <div className="flex items-center gap-1.5 shrink-0">
                  {t.onRetry && (
                    <button
                      onClick={() => { t.onRetry?.(); dismiss(t.id); }}
                      className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md cursor-pointer transition-opacity hover:opacity-80"
                      style={{ color: c.color, background: `${c.color}18` }}
                      aria-label="Retry"
                    >
                      <RefreshCw className="w-3 h-3" />
                      Retry
                    </button>
                  )}
                  <button
                    onClick={() => dismiss(t.id)}
                    className="cursor-pointer transition-opacity hover:opacity-60"
                    style={{ color: "var(--color-text-3)" }}
                    aria-label="Dismiss notification"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

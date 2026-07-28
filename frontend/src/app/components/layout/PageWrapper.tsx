import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";

interface PageWrapperProps { children: React.ReactNode; }

const pageTransition = { duration: 0.28, ease: [0.22, 1, 0.36, 1] as [number,number,number,number] };
const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
};

export const PageWrapper = ({ children }: PageWrapperProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen" style={{ background: "var(--color-surface)" }}>
      <Sidebar />

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              className="fixed inset-0 z-30 md:hidden"
              style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
            />
            <motion.div
              initial={{ x: "-100%" }} animate={{ x: 0 }} exit={{ x: "-100%" }}
              transition={{ type: "spring", stiffness: 320, damping: 32 }}
              className="fixed top-0 bottom-0 left-0 w-[220px] z-40 md:hidden flex flex-col"
              style={{ background: "var(--color-surface-1)", borderRight: "1px solid var(--color-border)" }}
            >
              <div className="h-14 flex items-center justify-between px-4 shrink-0"
                style={{ borderBottom: "1px solid var(--color-border)" }}>
                <span className="text-[13px] font-semibold" style={{ color: "var(--color-text-1)" }}>AgentFleet</span>
                <button onClick={() => setMobileOpen(false)} className="cursor-pointer" style={{ color: "var(--color-text-3)" }}>
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto" onClick={() => setMobileOpen(false)}>
                <Sidebar />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar onMobileMenuToggle={() => setMobileOpen(true)} />
        <motion.main
          variants={pageVariants} initial="initial" animate="animate"
          transition={pageTransition}
          className="flex-1 overflow-y-auto"
          style={{ padding: "32px 32px 48px" }}
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
};

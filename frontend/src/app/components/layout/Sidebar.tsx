import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard, Truck, LineChart, GitFork,
  MessageSquare, Settings, ChevronLeft, ChevronRight,
} from "lucide-react";
import { cn } from "../../lib/utils";

const NAV = [
  { path: "/",          label: "Dashboard",  icon: LayoutDashboard },
  { path: "/fleet",     label: "Fleet",      icon: Truck },
  { path: "/analytics", label: "Analytics",  icon: LineChart },
  { path: "/workflow",  label: "Workflow",   icon: GitFork },
  { path: "/chat",      label: "AI Chat",    icon: MessageSquare },
  { path: "/settings",  label: "Settings",   icon: Settings },
];

export const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { pathname } = useLocation();

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 220 }}
      transition={{ type: "spring", stiffness: 340, damping: 32 }}
      className="hidden md:flex flex-col h-screen sticky top-0 shrink-0 z-20 overflow-hidden"
      style={{ background: "var(--color-surface-1)", borderRight: "1px solid var(--color-border)" }}
    >
      {/* Logo */}
      <div className="h-14 flex items-center justify-between px-4 shrink-0" style={{ borderBottom: "1px solid var(--color-border)" }}>
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-7.5 h-7.5 rounded-lg shrink-0 flex items-center justify-center text-white font-black text-[12px] tracking-tighter"
            style={{ background: "linear-gradient(135deg, var(--color-blue-light), var(--color-violet))", boxShadow: "0 0 16px rgba(59, 130, 246, 0.3)" }}>
            AF
          </div>
          <AnimatePresence initial={false}>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.18 }}
                className="text-[13px] font-bold tracking-tight whitespace-nowrap bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent"
              >
                AgentFleet
              </motion.span>
            )}
          </AnimatePresence>
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-5 h-5 flex items-center justify-center rounded-md transition-colors cursor-pointer shrink-0 hover:bg-zinc-800/40"
          style={{ color: "var(--color-text-3)" }}
        >
          {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {NAV.map(({ path, label, icon: Icon }) => {
          const active = pathname === path;
          return (
            <Link key={path} to={path}>
              <div className={cn(
                "relative flex items-center gap-3 px-2.5 py-2.5 rounded-lg transition-all duration-150 cursor-pointer group",
                active ? "text-white" : "hover:text-white"
              )}
                style={{
                  background: active ? "rgba(59, 130, 246, 0.06)" : "transparent",
                  color: active ? "var(--color-text-1)" : "var(--color-text-2)",
                }}
              >
                {active && (
                  <motion.div layoutId="nav-pill"
                    className="absolute inset-0 rounded-lg"
                    style={{ background: "rgba(59, 130, 246, 0.04)", border: "1px solid rgba(59, 130, 246, 0.18)", boxShadow: "0 0 16px -4px rgba(59, 130, 246, 0.15)" }}
                    transition={{ type: "spring", stiffness: 380, damping: 34 }}
                  />
                )}
                <Icon className={cn("w-4 h-4 shrink-0 relative z-10 transition-colors", active ? "text-blue" : "group-hover:text-white")}
                  style={{ color: active ? "var(--color-blue-light)" : undefined }} />
                <AnimatePresence initial={false}>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -6 }}
                      transition={{ duration: 0.15 }}
                      className="text-[13px] font-medium relative z-10 whitespace-nowrap"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="p-3 shrink-0" style={{ borderTop: "1px solid var(--color-border)" }}>
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-white font-bold text-[10px]"
            style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
            AD
          </div>
          <AnimatePresence initial={false}>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="flex flex-col overflow-hidden"
              >
                <span className="text-[12px] font-semibold truncate" style={{ color: "var(--color-text-1)" }}>Administrator</span>
                <span className="text-[10px] truncate" style={{ color: "var(--color-text-3)" }}>admin@agentfleet.io</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
};

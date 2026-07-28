import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, Terminal, Cpu, Zap } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  ts: string;
}

const SUGGESTIONS = [
  "Dispatch 2.5 tons from Chennai to Bangalore",
  "Check maintenance status for TN38AB1234",
  "Show fleet utilization for this week",
  "Optimize route for Coimbatore delivery",
];

const TypingDots = () => (
  <div className="flex items-center gap-1 py-1">
    {[0, 1, 2].map(i => (
      <motion.span key={i} className="w-1.5 h-1.5 rounded-full"
        style={{ background: "var(--color-text-3)" }}
        animate={{ opacity: [0.3, 1, 0.3], y: [0, -3, 0] }}
        transition={{ duration: 1, delay: i * 0.18, repeat: Infinity }}
      />
    ))}
  </div>
);

export const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([{
    role: "assistant",
    content: "Hello. I'm the Fleet Supervisor Agent — powered by Llama 3.3 via Groq. I can orchestrate deliveries, check vehicle health, analyze routes, and query fleet analytics. What would you like to do?",
    ts: "10:14 AM",
  }]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const send = (text?: string) => {
    const content = (text ?? input).trim();
    if (!content) return;
    const ts = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages(p => [...p, { role: "user", content, ts }]);
    setInput("");
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      setMessages(p => [...p, {
        role: "assistant",
        content: `[Supervisor Core] Received: "${content}"\n\nIntent classified → fleet_delivery. Initiating agent sequence: Dispatch → Route → Maintenance → Analytics → Customer. All agents responding nominally. Transaction logged to Supabase.`,
        ts: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }]);
    }, 1400);
  };

  const isEmpty = messages.length === 1 && !typing;

  return (
    <div className="max-w-3xl mx-auto h-[calc(100vh-112px)] flex flex-col gap-0">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}
        className="flex items-center justify-between px-5 py-4 rounded-t-2xl shrink-0"
        style={{ background: "var(--color-surface-1)", borderBottom: "1px solid var(--color-border)", border: "1px solid var(--color-border)", borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, rgba(79,142,247,0.2), rgba(124,106,247,0.2))", border: "1px solid rgba(124,106,247,0.3)" }}>
            <Sparkles className="w-4.5 h-4.5" style={{ color: "var(--color-violet)" }} />
          </div>
          <div>
            <p className="text-[13px] font-semibold" style={{ color: "var(--color-text-1)" }}>Fleet Supervisor</p>
            <p className="text-[11px]" style={{ color: "var(--color-text-3)" }}>Llama 3.3 · Groq · Intent Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold"
            style={{ color: "var(--color-emerald)" }}>
            <span className="relative w-2 h-2">
              <span className="absolute inset-0 rounded-full animate-ping" style={{ background: "var(--color-emerald)", opacity: 0.4 }} />
              <span className="relative block w-2 h-2 rounded-full" style={{ background: "var(--color-emerald)" }} />
            </span>
            Online
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px]"
            style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-3)" }}>
            <Cpu className="w-3 h-3" />
            ~320ms
          </div>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-6"
        style={{ background: "var(--color-surface-1)", borderLeft: "1px solid var(--color-border)", borderRight: "1px solid var(--color-border)" }}>

        {/* Empty state suggestions */}
        <AnimatePresence>
          {isEmpty && (
            <motion.div
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-6 pt-8"
            >
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, rgba(79,142,247,0.15), rgba(124,106,247,0.15))", border: "1px solid rgba(124,106,247,0.25)" }}>
                <Sparkles className="w-6 h-6" style={{ color: "var(--color-violet)" }} />
              </div>
              <div className="text-center">
                <p className="text-[15px] font-semibold" style={{ color: "var(--color-text-1)" }}>How can I help you today?</p>
                <p className="text-[12px] mt-1" style={{ color: "var(--color-text-3)" }}>Try one of these to get started</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
                {SUGGESTIONS.map(s => (
                  <button key={s} onClick={() => send(s)}
                    className="text-left px-4 py-3 rounded-xl text-[12px] font-medium transition-colors cursor-pointer hover:border-blue-500/30"
                    style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-2)" }}>
                    {s}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {messages.map((msg, i) => {
          const isUser = msg.role === "user";
          return (
            <motion.div key={i}
              initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
            >
              {/* Avatar */}
              <div className={`w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-white font-bold text-[10px] mt-0.5 ${isUser ? "" : ""}`}
                style={{ background: isUser ? "linear-gradient(135deg, #6366f1, #8b5cf6)" : "linear-gradient(135deg, rgba(79,142,247,0.3), rgba(124,106,247,0.3))", border: isUser ? "none" : "1px solid rgba(124,106,247,0.3)" }}>
                {isUser ? "AD" : <Sparkles className="w-3.5 h-3.5" style={{ color: "var(--color-violet)" }} />}
              </div>

              <div className={`flex flex-col gap-1 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-medium" style={{ color: "var(--color-text-3)" }}>
                    {isUser ? "You" : "Fleet Supervisor"}
                  </span>
                  <span className="text-[10px]" style={{ color: "var(--color-text-3)" }}>{msg.ts}</span>
                </div>
                <div className={`px-4 py-3 rounded-2xl text-[13px] leading-relaxed whitespace-pre-wrap ${isUser ? "rounded-tr-sm" : "rounded-tl-sm"}`}
                  style={isUser
                    ? { background: "linear-gradient(135deg, rgba(79,142,247,0.18), rgba(124,106,247,0.12))", border: "1px solid rgba(79,142,247,0.25)", color: "var(--color-text-1)" }
                    : { background: "var(--color-surface-2)", border: "1px solid var(--color-border)", color: "var(--color-text-1)" }
                  }>
                  {!isUser && (
                    <div className="flex items-center gap-1.5 mb-2 pb-2" style={{ borderBottom: "1px solid var(--color-border)" }}>
                      <Terminal className="w-3 h-3" style={{ color: "var(--color-violet)" }} />
                      <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--color-violet)" }}>Supervisor Output</span>
                    </div>
                  )}
                  {msg.content}
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Typing indicator */}
        <AnimatePresence>
          {typing && (
            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex gap-3">
              <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, rgba(79,142,247,0.3), rgba(124,106,247,0.3))", border: "1px solid rgba(124,106,247,0.3)" }}>
                <Sparkles className="w-3.5 h-3.5" style={{ color: "var(--color-violet)" }} />
              </div>
              <div className="px-4 py-3 rounded-2xl rounded-tl-sm"
                style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
                <TypingDots />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <motion.div
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.3 }}
        className="shrink-0 p-4 rounded-b-2xl"
        style={{ background: "var(--color-surface-1)", borderTop: "1px solid var(--color-border)", border: "1px solid var(--color-border)", borderTopLeftRadius: 0, borderTopRightRadius: 0 }}
      >
        <div className="flex items-center gap-3">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl transition-colors"
            style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}>
            <Zap className="w-4 h-4 shrink-0" style={{ color: "var(--color-text-3)" }} />
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
              placeholder="Ask the supervisor anything about your fleet..."
              className="flex-1 bg-transparent text-[13px] outline-none placeholder:text-[var(--color-text-3)]"
              style={{ color: "var(--color-text-1)" }}
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
            onClick={() => send()}
            disabled={!input.trim() || typing}
            className="w-10 h-10 rounded-xl flex items-center justify-center transition-opacity cursor-pointer disabled:opacity-40"
            style={{ background: "linear-gradient(135deg, #4f8ef7, #7c6af7)" }}
          >
            <Send className="w-4 h-4 text-white" />
          </motion.button>
        </div>
        <p className="text-[10px] mt-2 text-center" style={{ color: "var(--color-text-3)" }}>
          Press Enter to send · Shift+Enter for new line
        </p>
      </motion.div>
    </div>
  );
};

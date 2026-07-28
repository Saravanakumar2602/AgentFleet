import { Search, Bell } from "lucide-react";

interface NavbarProps {
  onMobileMenuToggle: () => void;
}

export const Navbar = ({ onMobileMenuToggle }: NavbarProps) => {
  return (
    <header
      className="h-14 sticky top-0 z-10 flex items-center justify-between px-6 shrink-0"
      style={{
        background: "rgba(10,10,15,0.8)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid var(--color-border)",
      }}
    >
      {/* Search */}
      <button
        onClick={onMobileMenuToggle}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-colors cursor-pointer group"
        style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
      >
        <Search className="w-3.5 h-3.5" style={{ color: "var(--color-text-3)" }} />
        <span className="text-[12px] hidden sm:block" style={{ color: "var(--color-text-3)" }}>
          Search anything...
        </span>
        <kbd className="hidden sm:flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded-md font-mono ml-8"
          style={{ background: "var(--color-surface)", color: "var(--color-text-3)", border: "1px solid var(--color-border)" }}>
          ⌘K
        </kbd>
      </button>

      {/* Right */}
      <div className="flex items-center gap-2">
        <button
          className="relative w-8 h-8 flex items-center justify-center rounded-lg transition-colors cursor-pointer"
          style={{ color: "var(--color-text-2)" }}
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full"
            style={{ background: "var(--color-blue)" }} />
        </button>

        <div className="w-px h-4 mx-1" style={{ background: "var(--color-border)" }} />

        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-[10px]"
            style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
            AD
          </div>
          <span className="text-[12px] font-medium hidden lg:block transition-colors"
            style={{ color: "var(--color-text-2)" }}>
            Administrator
          </span>
        </div>
      </div>
    </header>
  );
};

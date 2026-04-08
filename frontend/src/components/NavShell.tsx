import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Brain, Search, Upload, LogOut, LayoutDashboard, MessageSquare, Menu, X, BookOpen } from "lucide-react";

interface NavShellProps {
  currentView: string;
  onNavigate: (view: string) => void;
  onLogout: () => void;
  children: React.ReactNode;
}

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "documents", label: "Documents", icon: FileText },
  { id: "query", label: "AI Query", icon: MessageSquare },
  { id: "notes", label: "Notes", icon: BookOpen },
];

const NavShell = ({ currentView, onNavigate, onLogout, children }: NavShellProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background gradient-mesh">
      {/* Top bar */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-panel rounded-none border-t-0 border-x-0">
        <div className="flex items-center justify-between px-6 h-16">
          <div className="flex items-center gap-3">
            <Brain className="w-7 h-7 text-primary animate-pulse-glow" />
            <span className="font-heading font-bold text-lg text-foreground">DocuMind</span>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  currentView === item.id
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              onClick={onLogout}
              className="hidden md:flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 text-muted-foreground"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile nav */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed top-16 left-0 right-0 z-40 glass-panel rounded-none border-t-0 border-x-0 p-4 md:hidden"
          >
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => { onNavigate(item.id); setMobileOpen(false); }}
                className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  currentView === item.id ? "bg-primary/10 text-primary" : "text-muted-foreground"
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
            <button
              onClick={onLogout}
              className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-sm text-destructive mt-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="pt-20 pb-8 px-4 md:px-8 max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  );
};

export default NavShell;

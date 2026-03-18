"use client";

import { MessageSquare, FileText, BarChart2, Wrench, Settings, ChevronLeft, ChevronRight } from "lucide-react";
import { useAppStore, type ActiveView } from "@/store/app-store";
import { cn } from "@/lib/utils";

const navItems: { id: ActiveView; label: string; Icon: React.ComponentType<{ size?: number; className?: string }> }[] = [
  { id: "chat", label: "对话", Icon: MessageSquare },
  { id: "resume", label: "简历", Icon: FileText },
  { id: "tracker", label: "投递", Icon: BarChart2 },
  { id: "skills", label: "技能", Icon: Wrench },
];

export function Sidebar() {
  const { activeView, setActiveView, sidebarCollapsed, toggleSidebar } =
    useAppStore();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen border-r transition-all duration-300 flex-shrink-0",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
      style={{
        backgroundColor: "var(--secondary)",
        borderColor: "var(--border)",
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center h-16 px-4 border-b gap-3"
        style={{ borderColor: "var(--border)" }}
      >
        <div
          className="flex items-center justify-center w-8 h-8 rounded-lg font-bold text-sm flex-shrink-0"
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          JF
        </div>
        {!sidebarCollapsed && (
          <span className="font-bold text-base" style={{ color: "var(--foreground)" }}>
            JobFlow
          </span>
        )}
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems.map(({ id, label, Icon }) => (
          <button
            key={id}
            onClick={() => setActiveView(id)}
            className={cn(
              "flex items-center w-full rounded-md transition-colors cursor-pointer",
              sidebarCollapsed ? "p-2 justify-center" : "px-3 py-2 gap-3",
              activeView === id
                ? "font-medium"
                : "hover:opacity-80"
            )}
            style={{
              backgroundColor:
                activeView === id ? "var(--accent)" : "transparent",
              color:
                activeView === id
                  ? "var(--accent-foreground)"
                  : "var(--muted-foreground)",
            }}
            title={sidebarCollapsed ? label : undefined}
          >
            <Icon size={18} className="flex-shrink-0" />
            {!sidebarCollapsed && (
              <span className="text-sm">{label}</span>
            )}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div
        className="px-2 py-4 border-t space-y-1"
        style={{ borderColor: "var(--border)" }}
      >
        <button
          className={cn(
            "flex items-center w-full rounded-md transition-colors cursor-pointer",
            sidebarCollapsed ? "p-2 justify-center" : "px-3 py-2 gap-3"
          )}
          style={{ color: "var(--muted-foreground)" }}
          title={sidebarCollapsed ? "设置" : undefined}
        >
          <Settings size={18} />
          {!sidebarCollapsed && <span className="text-sm">设置</span>}
        </button>
        <button
          onClick={toggleSidebar}
          className={cn(
            "flex items-center w-full rounded-md transition-colors cursor-pointer",
            sidebarCollapsed ? "p-2 justify-center" : "px-3 py-2 gap-3"
          )}
          style={{ color: "var(--muted-foreground)" }}
        >
          {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          {!sidebarCollapsed && <span className="text-sm">折叠</span>}
        </button>
      </div>
    </aside>
  );
}

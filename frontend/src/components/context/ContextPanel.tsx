"use client";

import { PanelRightClose, PanelRightOpen } from "lucide-react";
import { ResumeSummaryCard } from "./ResumeSummaryCard";
import { MatchScoreCard } from "./MatchScoreCard";
import { useAppStore } from "@/store/app-store";
import { cn } from "@/lib/utils";

export function ContextPanel() {
  const { contextPanelOpen, toggleContextPanel, isStreaming } = useAppStore();

  return (
    <aside
      className={cn(
        "flex flex-col h-screen border-l transition-all duration-300 flex-shrink-0",
        contextPanelOpen ? "w-80" : "w-10"
      )}
      style={{
        backgroundColor: "var(--background)",
        borderColor: "var(--border)",
      }}
    >
      {/* Toggle button */}
      <div
        className="flex items-center justify-end h-16 px-2 border-b flex-shrink-0"
        style={{ borderColor: "var(--border)" }}
      >
        <button
          onClick={toggleContextPanel}
          className="p-1.5 rounded-md transition-colors cursor-pointer hover:opacity-80"
          style={{ color: "var(--muted-foreground)" }}
          title={contextPanelOpen ? "收起面板" : "展开面板"}
        >
          {contextPanelOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
        </button>
      </div>

      {contextPanelOpen && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Active status */}
          {isStreaming && (
            <div
              className="flex items-center gap-2 px-3 py-2 rounded-md text-xs"
              style={{
                backgroundColor: "var(--muted)",
                color: "var(--muted-foreground)",
              }}
            >
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: "var(--primary)" }} />
              Agent 正在思考...
            </div>
          )}

          <ResumeSummaryCard />
          <MatchScoreCard />
        </div>
      )}
    </aside>
  );
}

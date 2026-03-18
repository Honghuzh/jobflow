"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Search, BarChart2, FileText, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ToolCall } from "@/store/app-store";

const toolIcons: Record<string, React.ComponentType<{ size?: number }>> = {
  parse_jd: Search,
  match_score: BarChart2,
  parse_resume: FileText,
};

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
}

export function ToolCallDisplay({ toolCalls }: ToolCallDisplayProps) {
  const [expanded, setExpanded] = useState(false);

  if (!toolCalls.length) return null;

  return (
    <div
      className="mt-2 rounded-md border overflow-hidden text-xs"
      style={{ borderColor: "var(--border)" }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-2 text-left transition-colors cursor-pointer"
        style={{
          backgroundColor: "var(--muted)",
          color: "var(--muted-foreground)",
        }}
      >
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <span>工具调用 ({toolCalls.length})</span>
      </button>
      {expanded && (
        <div
          className="divide-y"
          style={{ borderColor: "var(--border)" }}
        >
          {toolCalls.map((tc, i) => {
            const Icon = toolIcons[tc.name] ?? Wrench;
            return (
              <div key={i} className="px-3 py-2 space-y-1">
                <div className="flex items-center gap-2 font-medium" style={{ color: "var(--foreground)" }}>
                  <Icon size={12} />
                  <span>{tc.name}</span>
                </div>
                <pre
                  className="text-xs overflow-x-auto rounded p-1"
                  style={{ backgroundColor: "var(--secondary)", color: "var(--muted-foreground)" }}
                >
                  {JSON.stringify(tc.args, null, 2)}
                </pre>
                {tc.result !== undefined && (
                  <div>
                    <span style={{ color: "var(--muted-foreground)" }}>结果：</span>
                    <pre
                      className="text-xs overflow-x-auto rounded p-1 mt-1"
                      style={{ backgroundColor: "var(--secondary)", color: "var(--foreground)" }}
                    >
                      {typeof tc.result === "string"
                        ? tc.result
                        : JSON.stringify(tc.result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

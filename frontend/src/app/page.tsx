"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ContextPanel } from "@/components/context/ContextPanel";
import { TrackerView } from "@/components/tracker/TrackerView";
import { ResumeView } from "@/components/resume/ResumeView";
import { useAppStore } from "@/store/app-store";

export default function Home() {
  const activeView = useAppStore((s) => s.activeView);

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: "var(--background)", color: "var(--foreground)" }}>
      <Sidebar />
      <main className="flex-1 flex overflow-hidden">
        {activeView === "chat" && <ChatPanel />}
        {activeView === "tracker" && <TrackerView />}
        {activeView === "resume" && <ResumeView />}
        {activeView === "skills" && (
          <div className="flex-1 flex items-center justify-center" style={{ color: "var(--muted-foreground)" }}>
            <p>技能库功能即将上线</p>
          </div>
        )}
        <ContextPanel />
      </main>
    </div>
  );
}

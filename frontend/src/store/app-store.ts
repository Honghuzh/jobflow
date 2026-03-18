import { create } from "zustand";
import { generateId } from "@/lib/utils";

export type ActiveView = "chat" | "tracker" | "resume" | "skills";

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: unknown;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: ToolCall[];
  timestamp: number;
  isLoading?: boolean;
}

interface AppState {
  // Navigation
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;

  // Chat
  messages: Message[];
  threadId: string | null;
  isStreaming: boolean;
  addMessage: (msg: Omit<Message, "id" | "timestamp">) => string;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setStreaming: (v: boolean) => void;
  clearMessages: () => void;
  setThreadId: (id: string | null) => void;

  // Resume
  resumeData: Record<string, unknown> | null;
  setResumeData: (data: Record<string, unknown> | null) => void;

  // Match Score
  matchScore: Record<string, unknown> | null;
  setMatchScore: (score: Record<string, unknown> | null) => void;

  // Context Panel
  contextPanelOpen: boolean;
  toggleContextPanel: () => void;

  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeView: "chat",
  setActiveView: (view) => set({ activeView: view }),

  messages: [],
  threadId: null,
  isStreaming: false,

  addMessage: (msg) => {
    const id = generateId();
    set((state) => ({
      messages: [
        ...state.messages,
        { ...msg, id, timestamp: Date.now() },
      ],
    }));
    return id;
  },

  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, ...updates } : m
      ),
    })),

  setStreaming: (v) => set({ isStreaming: v }),
  clearMessages: () => set({ messages: [], threadId: null }),
  setThreadId: (id) => set({ threadId: id }),

  resumeData: null,
  setResumeData: (data) => set({ resumeData: data }),

  matchScore: null,
  setMatchScore: (score) => set({ matchScore: score }),

  contextPanelOpen: true,
  toggleContextPanel: () =>
    set((state) => ({ contextPanelOpen: !state.contextPanelOpen })),

  sidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}));

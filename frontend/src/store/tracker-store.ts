import { create } from "zustand";
import { generateId } from "@/lib/utils";
import { getTrackerList } from "@/lib/api";

export type JobStatus =
  | "wishlist"
  | "applied"
  | "interview"
  | "offer"
  | "rejected";

export interface JobEntry {
  id: string;
  company: string;
  position: string;
  status: JobStatus;
  appliedDate: string;
  notes: string;
  url?: string;
}

interface TrackerState {
  jobs: JobEntry[];
  fetchError: string | null;
  addJob: (job: Omit<JobEntry, "id">) => void;
  updateJobStatus: (id: string, status: JobStatus) => void;
  removeJob: (id: string) => void;
  fetchJobs: () => Promise<void>;
}

export const useTrackerStore = create<TrackerState>((set) => ({
  jobs: [],
  fetchError: null,

  addJob: (job) =>
    set((state) => ({
      jobs: [...state.jobs, { ...job, id: generateId() }],
    })),

  updateJobStatus: (id, status) =>
    set((state) => ({
      jobs: state.jobs.map((j) => (j.id === id ? { ...j, status } : j)),
    })),

  removeJob: (id) =>
    set((state) => ({
      jobs: state.jobs.filter((j) => j.id !== id),
    })),

  fetchJobs: async () => {
    try {
      const data = await getTrackerList();
      if (Array.isArray(data)) {
        set({ jobs: data as JobEntry[], fetchError: null });
      }
    } catch (err) {
      set({
        fetchError: err instanceof Error ? err.message : "获取投递列表失败",
      });
    }
  },
}));

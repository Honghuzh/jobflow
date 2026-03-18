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
  addJob: (job: Omit<JobEntry, "id">) => void;
  updateJobStatus: (id: string, status: JobStatus) => void;
  removeJob: (id: string) => void;
  fetchJobs: () => Promise<void>;
}

export const useTrackerStore = create<TrackerState>((set) => ({
  jobs: [],

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
        set({ jobs: data as JobEntry[] });
      }
    } catch {
      // Use local state if API fails
    }
  },
}));

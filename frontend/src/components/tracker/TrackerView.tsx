"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { useTrackerStore, type JobEntry, type JobStatus } from "@/store/tracker-store";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatDate, todayISO } from "@/lib/utils";

const columns: { id: JobStatus; label: string; color: string }[] = [
  { id: "wishlist", label: "待投递", color: "default" },
  { id: "applied", label: "已投递", color: "default" },
  { id: "interview", label: "面试中", color: "warning" },
  { id: "offer", label: "Offer", color: "success" },
  { id: "rejected", label: "拒绝", color: "destructive" },
];

interface AddJobForm {
  company: string;
  position: string;
  status: JobStatus;
  appliedDate: string;
  notes: string;
  url: string;
}

export function TrackerView() {
  const { jobs, fetchError, addJob, updateJobStatus, removeJob, fetchJobs } = useTrackerStore();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<AddJobForm>({
    company: "",
    position: "",
    status: "wishlist",
    appliedDate: todayISO(),
    notes: "",
    url: "",
  });

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleAdd = () => {
    if (!form.company || !form.position) return;
    addJob({ ...form });
    setForm({
      company: "",
      position: "",
      status: "wishlist",
      appliedDate: todayISO(),
      notes: "",
      url: "",
    });
    setShowForm(false);
  };

  const statCounts = columns.reduce(
    (acc, col) => {
      acc[col.id] = jobs.filter((j) => j.status === col.id).length;
      return acc;
    },
    {} as Record<JobStatus, number>
  );

  return (
    <div
      className="flex-1 flex flex-col overflow-hidden"
      style={{ backgroundColor: "var(--background)" }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-4 border-b flex-shrink-0"
        style={{ borderColor: "var(--border)" }}
      >
        <div>
          <h1 className="font-semibold text-base" style={{ color: "var(--foreground)" }}>
            投递进度看板
          </h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            共 {jobs.length} 个岗位
          </p>
        </div>
        <Button size="sm" onClick={() => setShowForm(true)}>
          <Plus size={16} className="mr-1" />
          添加投递
        </Button>
      </div>

      {/* API error notice */}
      {fetchError && (
        <div
          className="mx-6 mt-3 px-3 py-2 rounded-md text-xs"
          style={{ backgroundColor: "var(--muted)", color: "var(--muted-foreground)" }}
        >
          ⚠️ 无法从服务器加载投递数据（{fetchError}），当前显示本地数据。
        </div>
      )}

      {/* Stats */}
      <div
        className="flex gap-4 px-6 py-3 border-b flex-shrink-0 overflow-x-auto"
        style={{ borderColor: "var(--border)" }}
      >
        {columns.map((col) => (
          <div key={col.id} className="flex items-center gap-2 text-sm flex-shrink-0">
            <Badge variant={col.color as "default" | "success" | "warning" | "destructive"}>
              {col.label}
            </Badge>
            <span style={{ color: "var(--foreground)", fontWeight: 600 }}>
              {statCounts[col.id]}
            </span>
          </div>
        ))}
      </div>

      {/* Add form */}
      {showForm && (
        <div
          className="mx-6 mt-4 p-4 rounded-lg border"
          style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
        >
          <h3 className="text-sm font-medium mb-3" style={{ color: "var(--foreground)" }}>
            添加投递记录
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <input
              className="border rounded-md px-3 py-2 text-sm outline-none"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              placeholder="公司名称 *"
              value={form.company}
              onChange={(e) => setForm({ ...form, company: e.target.value })}
            />
            <input
              className="border rounded-md px-3 py-2 text-sm outline-none"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              placeholder="岗位名称 *"
              value={form.position}
              onChange={(e) => setForm({ ...form, position: e.target.value })}
            />
            <input
              type="date"
              className="border rounded-md px-3 py-2 text-sm outline-none"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              value={form.appliedDate}
              onChange={(e) => setForm({ ...form, appliedDate: e.target.value })}
            />
            <select
              className="border rounded-md px-3 py-2 text-sm outline-none"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as JobStatus })}
            >
              {columns.map((col) => (
                <option key={col.id} value={col.id}>
                  {col.label}
                </option>
              ))}
            </select>
            <input
              className="border rounded-md px-3 py-2 text-sm outline-none col-span-2"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              placeholder="职位链接"
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
            />
            <textarea
              className="border rounded-md px-3 py-2 text-sm outline-none col-span-2 resize-none"
              style={{
                borderColor: "var(--border)",
                backgroundColor: "var(--background)",
                color: "var(--foreground)",
              }}
              placeholder="备注"
              rows={2}
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={handleAdd}>确认添加</Button>
            <Button size="sm" variant="ghost" onClick={() => setShowForm(false)}>
              取消
            </Button>
          </div>
        </div>
      )}

      {/* Kanban */}
      <div className="flex-1 overflow-x-auto p-6">
        <div className="flex gap-4 h-full" style={{ minWidth: "800px" }}>
          {columns.map((col) => {
            const colJobs = jobs.filter((j) => j.status === col.id);
            return (
              <div
                key={col.id}
                className="flex-1 flex flex-col rounded-xl min-w-0"
                style={{ backgroundColor: "var(--secondary)", minWidth: "160px" }}
              >
                <div className="px-4 py-3 flex items-center justify-between">
                  <span className="text-sm font-medium" style={{ color: "var(--secondary-foreground)" }}>
                    {col.label}
                  </span>
                  <Badge variant={col.color as "default" | "success" | "warning" | "destructive"}>
                    {colJobs.length}
                  </Badge>
                </div>
                <div className="flex-1 px-3 pb-3 space-y-2 overflow-y-auto">
                  {colJobs.map((job) => (
                    <JobCard
                      key={job.id}
                      job={job}
                      onStatusChange={updateJobStatus}
                      onRemove={removeJob}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function JobCard({
  job,
  onStatusChange,
  onRemove,
}: {
  job: JobEntry;
  onStatusChange: (id: string, status: JobStatus) => void;
  onRemove: (id: string) => void;
}) {
  const nextStatus: Record<JobStatus, JobStatus | null> = {
    wishlist: "applied",
    applied: "interview",
    interview: "offer",
    offer: null,
    rejected: null,
  };

  const next = nextStatus[job.status];

  return (
    <div
      className="rounded-lg p-3 border"
      style={{
        backgroundColor: "var(--card)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex items-start justify-between gap-1">
        <div className="min-w-0">
          <p className="text-sm font-medium truncate" style={{ color: "var(--foreground)" }}>
            {job.company}
          </p>
          <p className="text-xs truncate mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            {job.position}
          </p>
        </div>
        <button
          onClick={() => onRemove(job.id)}
          className="p-0.5 rounded cursor-pointer hover:opacity-70 flex-shrink-0"
          style={{ color: "var(--muted-foreground)" }}
        >
          <Trash2 size={12} />
        </button>
      </div>
      <p className="text-xs mt-2" style={{ color: "var(--muted-foreground)" }}>
        {formatDate(job.appliedDate)}
      </p>
      {next && (
        <button
          onClick={() => onStatusChange(job.id, next)}
          className="mt-2 text-xs px-2 py-1 rounded cursor-pointer hover:opacity-80 transition-colors w-full"
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          推进到下一阶段
        </button>
      )}
    </div>
  );
}

"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Upload, FileText, RefreshCw } from "lucide-react";
import { useAppStore } from "@/store/app-store";
import { uploadResume } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";

export function ResumeView() {
  const { resumeData, setResumeData } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const result = await uploadResume(file);
      if (result && typeof result === "object") {
        setResumeData(result as Record<string, unknown>);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

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
        <h1 className="font-semibold text-base" style={{ color: "var(--foreground)" }}>
          简历管理
        </h1>
        {resumeData && (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            <RefreshCw size={16} className="mr-1" />
            重新上传
          </Button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {/* Upload area */}
        {!resumeData ? (
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "flex flex-col items-center justify-center border-2 border-dashed rounded-xl cursor-pointer transition-colors",
              "h-64"
            )}
            style={{
              borderColor: isDragging ? "var(--primary)" : "var(--border)",
              backgroundColor: isDragging ? "var(--secondary)" : "transparent",
            }}
          >
            {isUploading ? (
              <div className="flex flex-col items-center gap-3">
                <div
                  className="w-10 h-10 border-4 border-t-transparent rounded-full animate-spin"
                  style={{ borderColor: "var(--primary)", borderTopColor: "transparent" }}
                />
                <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                  正在解析...
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <Upload size={40} style={{ color: "var(--muted-foreground)" }} />
                <div className="text-center">
                  <p className="font-medium text-sm" style={{ color: "var(--foreground)" }}>
                    点击或拖拽上传简历
                  </p>
                  <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
                    支持 TXT, MD, PDF, DOC, DOCX（最大 10MB）
                  </p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <ResumePreview data={resumeData} />
        )}

        {error && (
          <p className="text-sm mt-4 text-center" style={{ color: "var(--destructive)" }}>
            {error}
          </p>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md,.pdf,.doc,.docx"
        className="hidden"
        onChange={handleFileChange}
      />
    </div>
  );
}

function ResumePreview({ data }: { data: Record<string, unknown> }) {
  const name = (data.name as string) ?? "候选人";
  const email = (data.email as string) ?? "";
  const phone = (data.phone as string) ?? "";
  const skills = (data.skills as string[]) ?? [];
  const experience = (data.experience as string) ?? "";
  const education = (data.education as string) ?? "";
  const summary = (data.summary as string) ?? "";

  return (
    <div className="space-y-4 max-w-2xl mx-auto">
      {/* Basic info */}
      <div
        className="rounded-xl p-5 border"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
      >
        <div className="flex items-start gap-4">
          <div
            className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0"
            style={{
              backgroundColor: "var(--primary)",
              color: "var(--primary-foreground)",
            }}
          >
            {name[0] ?? "?"}
          </div>
          <div>
            <h2 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
              {name}
            </h2>
            <div className="flex flex-col gap-0.5 mt-1">
              {email && (
                <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                  📧 {email}
                </span>
              )}
              {phone && (
                <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                  📱 {phone}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      {summary && (
        <Section title="个人简介">
          <p className="text-sm leading-relaxed" style={{ color: "var(--foreground)" }}>
            {summary}
          </p>
        </Section>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <Section title="技能">
          <div className="flex flex-wrap gap-2">
            {skills.map((s) => (
              <Badge key={s} variant="default">
                <FileText size={10} className="mr-1" />
                {s}
              </Badge>
            ))}
          </div>
        </Section>
      )}

      {/* Experience */}
      {experience && (
        <Section title="工作经历">
          <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--foreground)" }}>
            {experience}
          </p>
        </Section>
      )}

      {/* Education */}
      {education && (
        <Section title="教育背景">
          <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--foreground)" }}>
            {education}
          </p>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      className="rounded-xl p-4 border"
      style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
    >
      <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>
        {title}
      </h3>
      {children}
    </div>
  );
}

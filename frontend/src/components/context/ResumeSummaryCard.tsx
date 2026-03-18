"use client";

import { Upload } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useAppStore } from "@/store/app-store";

export function ResumeSummaryCard() {
  const resumeData = useAppStore((s) => s.resumeData);

  if (!resumeData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>简历摘要</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className="flex flex-col items-center gap-2 py-4 text-center"
            style={{ color: "var(--muted-foreground)" }}
          >
            <Upload size={24} />
            <p className="text-xs">暂未上传简历</p>
            <p className="text-xs">在对话中上传 PDF/TXT/MD 文件</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const name = (resumeData.name as string) ?? "候选人";
  const email = (resumeData.email as string) ?? "";
  const phone = (resumeData.phone as string) ?? "";
  const skills = (resumeData.skills as string[]) ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>简历摘要</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="font-medium text-sm" style={{ color: "var(--foreground)" }}>
            {name}
          </p>
          {email && (
            <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
              {email}
            </p>
          )}
          {phone && (
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              {phone}
            </p>
          )}
        </div>
        {skills.length > 0 && (
          <div>
            <p className="text-xs font-medium mb-1.5" style={{ color: "var(--muted-foreground)" }}>
              技能
            </p>
            <div className="flex flex-wrap gap-1">
              {skills.slice(0, 10).map((skill) => (
                <Badge key={skill} variant="default">
                  {skill}
                </Badge>
              ))}
              {skills.length > 10 && (
                <Badge variant="default">+{skills.length - 10}</Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

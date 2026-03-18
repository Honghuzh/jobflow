"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Progress } from "@/components/ui/Progress";
import { useAppStore } from "@/store/app-store";

interface ScoreDimension {
  label: string;
  score: number;
}

export function MatchScoreCard() {
  const matchScore = useAppStore((s) => s.matchScore);

  if (!matchScore) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>匹配度评分</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-center py-4" style={{ color: "var(--muted-foreground)" }}>
            请先上传简历并分析职位
          </p>
        </CardContent>
      </Card>
    );
  }

  const overallScore = (matchScore.overall_score as number) ?? 0;
  const dimensions: ScoreDimension[] = [
    { label: "技术关键词", score: (matchScore.keyword_score as number) ?? 0 },
    { label: "工作经验", score: (matchScore.experience_score as number) ?? 0 },
    { label: "教育背景", score: (matchScore.education_score as number) ?? 0 },
  ];
  const matchedKeywords = (matchScore.matched_keywords as string[]) ?? [];
  const missingKeywords = (matchScore.missing_keywords as string[]) ?? [];
  const suggestions = (matchScore.suggestions as string[]) ?? [];

  // Circle progress
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (overallScore / 100) * circumference;

  const scoreColor =
    overallScore >= 80
      ? "var(--primary)"
      : overallScore >= 60
      ? "#f59e0b"
      : "#ef4444";

  return (
    <Card>
      <CardHeader>
        <CardTitle>匹配度评分</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Circular progress */}
        <div className="flex justify-center">
          <div className="relative w-24 h-24">
            <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                fill="none"
                strokeWidth="8"
                stroke="var(--secondary)"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                fill="none"
                strokeWidth="8"
                stroke={scoreColor}
                strokeDasharray={circumference}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                className="transition-all duration-500"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-bold" style={{ color: scoreColor }}>
                {overallScore}
              </span>
              <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                分
              </span>
            </div>
          </div>
        </div>

        {/* Dimensions */}
        <div className="space-y-2">
          {dimensions.map(({ label, score }) => (
            <div key={label}>
              <div className="flex justify-between text-xs mb-1">
                <span style={{ color: "var(--muted-foreground)" }}>{label}</span>
                <span style={{ color: "var(--foreground)" }}>{score}%</span>
              </div>
              <Progress value={score} />
            </div>
          ))}
        </div>

        {/* Keywords */}
        {matchedKeywords.length > 0 && (
          <div>
            <p className="text-xs font-medium mb-1" style={{ color: "var(--muted-foreground)" }}>
              匹配关键词
            </p>
            <div className="flex flex-wrap gap-1">
              {matchedKeywords.slice(0, 5).map((kw) => (
                <Badge key={kw} variant="success">{kw}</Badge>
              ))}
            </div>
          </div>
        )}

        {missingKeywords.length > 0 && (
          <div>
            <p className="text-xs font-medium mb-1" style={{ color: "var(--muted-foreground)" }}>
              缺失关键词
            </p>
            <div className="flex flex-wrap gap-1">
              {missingKeywords.slice(0, 5).map((kw) => (
                <Badge key={kw} variant="destructive">{kw}</Badge>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div>
            <p className="text-xs font-medium mb-1" style={{ color: "var(--muted-foreground)" }}>
              优化建议
            </p>
            <ul className="text-xs space-y-1 list-disc list-inside" style={{ color: "var(--foreground)" }}>
              {suggestions.slice(0, 3).map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

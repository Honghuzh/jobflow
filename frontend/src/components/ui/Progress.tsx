import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number; // 0-100
  className?: string;
  color?: string;
}

export function Progress({ value, className, color }: ProgressProps) {
  const clampedValue = Math.max(0, Math.min(100, value));
  return (
    <div
      className={cn("w-full rounded-full h-2", className)}
      style={{ backgroundColor: "var(--secondary)" }}
    >
      <div
        className="h-2 rounded-full transition-all"
        style={{
          width: `${clampedValue}%`,
          backgroundColor: color ?? "var(--primary)",
        }}
      />
    </div>
  );
}

import { cn } from "@/lib/utils";

interface AvatarProps {
  initials?: string;
  className?: string;
  variant?: "user" | "assistant";
}

export function Avatar({ initials, className, variant = "user" }: AvatarProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold flex-shrink-0",
        className
      )}
      style={{
        backgroundColor:
          variant === "user" ? "var(--primary)" : "var(--secondary)",
        color:
          variant === "user"
            ? "var(--primary-foreground)"
            : "var(--secondary-foreground)",
      }}
    >
      {initials ?? (variant === "user" ? "我" : "AI")}
    </div>
  );
}

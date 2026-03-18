"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Avatar } from "@/components/ui/Avatar";
import { ToolCallDisplay } from "./ToolCallDisplay";
import type { Message } from "@/store/app-store";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center py-2">
        <span
          className="text-xs px-3 py-1 rounded-full"
          style={{
            backgroundColor: "var(--muted)",
            color: "var(--muted-foreground)",
          }}
        >
          {message.content}
        </span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex gap-3 px-4 py-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <Avatar variant={isUser ? "user" : "assistant"} />
      <div className={cn("flex flex-col max-w-[75%]", isUser ? "items-end" : "items-start")}>
        <div
          className={cn("rounded-2xl px-4 py-2 text-sm", isUser ? "rounded-tr-sm" : "rounded-tl-sm")}
          style={{
            backgroundColor: isUser ? "var(--primary)" : "var(--secondary)",
            color: isUser ? "var(--primary-foreground)" : "var(--secondary-foreground)",
          }}
        >
          {message.isLoading ? (
            <div className="flex gap-1 items-center py-1">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{
                    backgroundColor: "var(--muted-foreground)",
                    animationDelay: `${i * 0.15}s`,
                  }}
                />
              ))}
            </div>
          ) : isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="w-full mt-1">
            <ToolCallDisplay toolCalls={message.toolCalls} />
          </div>
        )}
        <span
          className="text-xs mt-1 px-1"
          style={{ color: "var(--muted-foreground)" }}
        >
          {new Date(message.timestamp).toLocaleTimeString("zh-CN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}

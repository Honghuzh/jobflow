"use client";

import { useRef, useState, KeyboardEvent, ChangeEvent } from "react";
import { Send, Paperclip, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string, file?: File) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed && !file) return;
    onSend(trimmed || (file ? `[上传文件: ${file.name}]` : ""), file ?? undefined);
    setValue("");
    setFile(null);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  };

  return (
    <div
      className="border-t p-4"
      style={{ borderColor: "var(--border)", backgroundColor: "var(--background)" }}
    >
      {file && (
        <div
          className="flex items-center gap-2 mb-2 px-3 py-1.5 rounded-md w-fit text-xs"
          style={{ backgroundColor: "var(--secondary)", color: "var(--secondary-foreground)" }}
        >
          <Paperclip size={12} />
          <span>{file.name}</span>
          <button
            onClick={() => setFile(null)}
            className="cursor-pointer hover:opacity-70"
          >
            <X size={12} />
          </button>
        </div>
      )}
      <div
        className="flex items-end gap-2 rounded-xl border px-3 py-2"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--background)" }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.md,.pdf,.doc,.docx"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className={cn(
            "p-1.5 rounded-md transition-colors cursor-pointer flex-shrink-0",
            "hover:opacity-80 disabled:opacity-50"
          )}
          style={{ color: "var(--muted-foreground)" }}
        >
          <Paperclip size={18} />
        </button>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
          placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
          className="flex-1 resize-none bg-transparent outline-none text-sm py-1 disabled:opacity-50"
          style={{ color: "var(--foreground)", minHeight: "28px", maxHeight: "200px" }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || (!value.trim() && !file)}
          className={cn(
            "p-1.5 rounded-md transition-colors cursor-pointer flex-shrink-0",
            "hover:opacity-80 disabled:opacity-40"
          )}
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          {disabled ? (
            <div
              className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
              style={{ borderColor: "var(--primary-foreground)" }}
            />
          ) : (
            <Send size={16} />
          )}
        </button>
      </div>
      <p className="text-xs mt-1 text-center" style={{ color: "var(--muted-foreground)" }}>
        AI 可能会犯错，请核实重要信息
      </p>
    </div>
  );
}

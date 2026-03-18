"use client";

import { useEffect, useRef } from "react";
import { Plus } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { useAppStore } from "@/store/app-store";
import { streamMessage, uploadResume } from "@/lib/api";

export function ChatPanel() {
  const {
    messages,
    threadId,
    isStreaming,
    resumeData,
    addMessage,
    updateMessage,
    setStreaming,
    clearMessages,
    setThreadId,
    setResumeData,
  } = useAppStore();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text: string, file?: File) => {
    if (isStreaming) return;

    let currentResumeData = resumeData;

    // 1. 处理文件上传
    if (file) {
      try {
        const result = await uploadResume(file);
        if (result && typeof result === "object") {
          const formattedResult = result as Record<string, unknown>;
          setResumeData(formattedResult);
          currentResumeData = formattedResult;
        }
        addMessage({ role: "system", content: `简历 "${file.name}" 上传成功` });
      } catch (err) {
        addMessage({ role: "system", content: `文件上传失败` });
      }
      if (!text || text === `[上传文件: ${file.name}]`) return;
    }

    if (!text.trim()) return;

    // 2. 添加用户消息
    addMessage({ role: "user", content: text });

    // 3. 添加 AI 占位
    const assistantId = addMessage({
      role: "assistant",
      content: "",
      isLoading: true,
    });

    setStreaming(true);
    let accumulated = "";

    try {
      // 4. 调用流式 API
      await streamMessage(
        text,
        threadId ?? undefined,
        (token) => {
          accumulated += token;
          updateMessage(assistantId, { content: accumulated, isLoading: false });
        },
        (toolCall) => {
          const current = useAppStore.getState().messages.find(
            (m) => m.id === assistantId
          );
          updateMessage(assistantId, {
            toolCalls: [...(current?.toolCalls ?? []), toolCall],
          });
        },
        () => {
          updateMessage(assistantId, { isLoading: false });
          setStreaming(false);
          if (!accumulated) {
            updateMessage(assistantId, { content: "（无响应）" });
          }
        },
        (error) => {
          updateMessage(assistantId, {
            content: `错误: ${error}`,
            isLoading: false,
          });
          setStreaming(false);
        },
        currentResumeData // 传入简历数据
      );
    } catch (err) {
      updateMessage(assistantId, {
        content: `发送失败: ${err instanceof Error ? err.message : String(err)}`,
        isLoading: false,
      });
      setStreaming(false);
    }
  };

  const handleNewChat = () => {
    clearMessages();
    setThreadId(null);
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
          求职助手对话
        </h1>
        <button
          onClick={handleNewChat}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors cursor-pointer hover:opacity-80"
          style={{
            backgroundColor: "var(--secondary)",
            color: "var(--secondary-foreground)",
          }}
        >
          <Plus size={16} />
          新对话
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4">
        {messages.length === 0 ? (
          <div
            className="flex flex-col items-center justify-center h-full gap-4"
            style={{ color: "var(--muted-foreground)" }}
          >
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              JF
            </div>
            <div className="text-center">
              <p className="font-medium text-base" style={{ color: "var(--foreground)" }}>
                你好，我是 JobFlow 求职助手
              </p>
              <p className="text-sm mt-1">
                我可以帮你分析职位描述、优化简历、准备面试
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {[
                "分析这个职位描述",
                "帮我优化简历",
                "准备面试问题",
                "评估岗位匹配度",
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleSend(prompt)}
                  className="px-4 py-2.5 rounded-xl text-sm text-left transition-colors cursor-pointer hover:opacity-80 border"
                  style={{
                    backgroundColor: "var(--secondary)",
                    color: "var(--secondary-foreground)",
                    borderColor: "var(--border)",
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
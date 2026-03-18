const API_BASE = "/api";

export interface ChatResponse {
  message: string;
  thread_id: string;
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: unknown;
}

export async function sendMessage(
  message: string,
  threadId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function streamMessage(
  message: string,
  threadId?: string,
  onToken?: (token: string) => void,
  onToolCall?: (toolCall: any) => void,
  onDone?: () => void,
  onError?: (error: string) => void,
  resumeData?: any // <-- 新增：接收可选的简历数据
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message, 
        thread_id: threadId,
        resume_data: resumeData // <-- 新增：将简历数据发送给后端
      }),
    });

    if (!res.ok) {
      onError?.(`HTTP error! status: ${res.status}`);
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      onError?.("No response body");
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine || !trimmedLine.startsWith("data: ")) continue;

        const dataString = trimmedLine.slice(6).trim();
        
        if (dataString === "[DONE]") {
          onDone?.();
          return;
        }

        try {
          const parsed = JSON.parse(dataString);
          if (parsed.type === "done") {
            onDone?.();
            return;
          }

          if (parsed.type === "token" && Array.isArray(parsed.content)) {
            for (const item of parsed.content) {
              if (item.type === "text" && item.text) {
                onToken?.(item.text);
              }
            }
          } 
          else if (typeof parsed.content === "string") {
            onToken?.(parsed.content);
          }
          else if (parsed.type === "tool_call" || parsed.tool_call) {
            onToolCall?.(parsed.tool_call || parsed);
          }
          else if (parsed.type === "error") {
            onError?.(parsed.message || "后端返回错误");
          }
        } catch (parseErr) {
          // ignore
        }
      }
    }
    onDone?.();
  } catch (err) {
    onError?.(err instanceof Error ? err.message : String(err));
  }
}

export async function parseJD(text: string): Promise<unknown> {
  const res = await fetch(`${API_BASE}/jobs/parse-jd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function matchResume(
  resumeText: string,
  jdText: string
): Promise<unknown> {
  const res = await fetch(`${API_BASE}/jobs/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, jd_text: jdText }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function uploadResume(file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/resume/parse`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getCurrentResume(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/resume/current`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getTrackerStats(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/tracker/stats`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getTrackerList(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/tracker/list`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function updateTrackerStatus(
  id: string,
  status: string
): Promise<unknown> {
  const res = await fetch(`${API_BASE}/tracker/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, status }),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getSkills(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/skills`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getModels(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

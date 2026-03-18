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
  onToolCall?: (toolCall: ToolCall) => void,
  onDone?: () => void,
  onError?: (error: string) => void
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, thread_id: threadId }),
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
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          if (data === "[DONE]") {
            onDone?.();
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.type === "token" && parsed.content) {
              onToken?.(parsed.content);
            } else if (parsed.type === "tool_call") {
              onToolCall?.(parsed.tool_call);
            } else if (parsed.type === "error") {
              onError?.(parsed.message);
            }
          } catch (parseErr) {
            // If it starts with '{' it likely should have been valid JSON — log it
            if (data.startsWith("{")) {
              console.warn("SSE: Failed to parse JSON event:", parseErr, data);
            }
            // Do not treat arbitrary plain text as a token to avoid echoing user input
          }
        }
      }
    }
    onDone?.();
  } catch (err) {
    const isNetworkError = err instanceof TypeError;
    onError?.(
      isNetworkError
        ? "无法连接到后端服务，请确认后端服务已启动"
        : err instanceof Error
        ? err.message
        : String(err)
    );
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
  const res = await fetch(`${API_BASE}/resume/upload`, {
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

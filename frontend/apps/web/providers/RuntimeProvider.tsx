"use client";

import type { ReactNode } from "react";
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
} from "@assistant-ui/react";

const ModelAdapter: ChatModelAdapter = {
  async run({ messages, abortSignal }) {
    // Forward the request to the backend A2A service
    const backendEndpoint = process.env.A2A_BACKEND_ENDPOINT || 'http://localhost:8000/a2a/messages';
    const result = await fetch(backendEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // forward the messages in the chat to the API
      body: JSON.stringify({
        messages,
      }),
      // if the user hits the "cancel" button or escape keyboard key, cancel the request
      signal: abortSignal,
    });

    if (!result.body) {
      throw new Error("No response body");
    }

    // Process the SSE stream to accumulate the full response
    const reader = result.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let accumulatedText = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep last incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove 'data: ' prefix
              
              // Skip empty data and [DONE] markers
              if (data.trim() && data.trim() !== '[DONE]') {
                // Accumulate the received text chunk
                accumulatedText += data;
              }
            }
          }
        }
        
        if (done) {
          // Process any remaining content in the buffer after stream ends
          if (buffer.trim()) {
            const remainingLines = buffer.split('\n');
            for (const line of remainingLines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6); // Remove 'data: ' prefix
                
                // Skip empty data and [DONE] markers
                if (data.trim() && data.trim() !== '[DONE]') {
                  // Accumulate the received text chunk
                  accumulatedText += data;
                }
              }
            }
          }
          break;
        }
      }
    } finally {
      reader.releaseLock();
    }
    
    // Try to parse as JSON to extract text content if it's in message format
    let responseText = accumulatedText;
    try {
      const parsed = JSON.parse(accumulatedText);
      if (parsed && typeof parsed === 'object') {
        // If it's an array of messages, extract text from text-type messages
        if (Array.isArray(parsed)) {
          const textMessages = parsed
            .filter((msg: any) => msg.type === 'text')
            .map((msg: any) => msg.text)
            .filter((text: any) => text);
          responseText = textMessages.join(' ');
        } else if (parsed.type === 'text' && parsed.text) {
          // If it's a single message object with text
          responseText = parsed.text;
        } else if (parsed.text) {
          // If it's an object with a text property
          responseText = parsed.text;
        }
      }
    } catch (e) {
      // If parsing fails, use the accumulated text as-is
      // This handles cases where the backend returns plain text
    }

    return {
      content: [
        {
          type: "text",
          text: responseText,
        },
      ],
    };
  },
};

export function RuntimeProvider({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const runtime = useLocalRuntime(ModelAdapter);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
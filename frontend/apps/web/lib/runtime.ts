import {
  useExternalStoreRuntime,
  type AssistantRuntime,
  type ThreadMessage,
  type AppendMessage,
  type ExternalStoreAdapter,
} from "@assistant-ui/react";

export interface A2ARuntimeConfig {
  endpoint?: string;
}

export const createA2ARuntime = (config: A2ARuntimeConfig = {}): AssistantRuntime => {
  const endpoint = config.endpoint || (typeof window !== 'undefined' ? (window as any).env?.NEXT_PUBLIC_A2A_ENDPOINT : undefined) || "http://localhost:8000/a2a/messages";
  
  // Create an external store adapter that will manage the thread state
  const adapter: ExternalStoreAdapter<ThreadMessage> = {
    isRunning: false,
    messages: [],
    setMessages: (messages) => {
      // Create a new array reference to ensure proper state updates
      adapter.messages = [...messages];
    },
    onImport: () => {},
    onCancel: async () => {},
    onNew: async (message) => {
      // First add the user message to the thread
      const userMessageId = `user-${Date.now()}`;
      const userMessage: ThreadMessage = {
        id: userMessageId,
        createdAt: new Date(),
        role: 'user',
        content: message.content as any, // Type assertion since AppendMessage content should be compatible
        attachments: [],
        metadata: {
          unstable_state: undefined,
          unstable_annotations: undefined,
          unstable_data: undefined,
          steps: undefined,
          submittedFeedback: undefined,
          custom: {}
        }
      } as any; // Using 'any' to bypass strict type checking temporarily
      
      // Add the user message to the thread
      if (adapter.messages && adapter.setMessages) {
        adapter.setMessages([...(adapter.messages || []), userMessage]);
      }
      
      // Convert ThreadMessage to the format expected by the A2A backend
      const a2aMessages = [message].map((msg) => {
        // Extract text content from the message
        let content = "";
        if (msg.content && msg.content.length > 0) {
          const firstContentPart = msg.content[0];
          if (firstContentPart && typeof firstContentPart === 'object' && 'text' in firstContentPart && firstContentPart.text) {
            content = firstContentPart.text as string;
          } else {
            content = JSON.stringify(firstContentPart);
          }
        }
        
        return {
          role: msg.role,
          content: content
        };
      });
      
      // Send request to A2A backend
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: a2aMessages }),
      });
      
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
      }
      
      if (!response.body) {
        throw new Error("No response body");
      }
      
      // Create an assistant message to accumulate the response
      let assistantMessageId = `assistant-${Date.now()}`;
      let accumulatedText = "";
      
      // Add a placeholder assistant message
      const placeholderAssistantMessage: ThreadMessage = {
        id: assistantMessageId,
        createdAt: new Date(),
        role: 'assistant',
        content: [{ type: 'text', text: '' }],
        status: { type: 'running' },
        metadata: {
          unstable_state: undefined,
          unstable_annotations: undefined,
          unstable_data: undefined,
          steps: undefined,
          submittedFeedback: undefined,
          custom: {}
        }
      } as any; // Using 'any' to bypass strict type checking temporarily
      
      // Add the placeholder assistant message to the thread
      if (adapter.messages && adapter.setMessages) {
        adapter.setMessages([...(adapter.messages || []), userMessage, placeholderAssistantMessage]);
      }
      
      // Process the SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      
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
                  
                  // Update the assistant message with the new accumulated text
                  const updatedAssistantMessage: ThreadMessage = {
                    id: assistantMessageId,
                    createdAt: new Date(),
                    role: 'assistant',
                    content: [{ type: 'text', text: accumulatedText }],
                    status: { type: 'running' },
                    metadata: {
                      unstable_state: undefined,
                      unstable_annotations: undefined,
                      unstable_data: undefined,
                      steps: undefined,
                      submittedFeedback: undefined,
                      custom: {}
                    }
                  } as any;
                  
                  // Update the messages array - replace the old assistant message with the updated one
                  if (adapter.messages && adapter.setMessages) {
                    const currentMessages = adapter.messages || [];
                    const updatedMessages = [...currentMessages.slice(0, -1), updatedAssistantMessage];
                    adapter.setMessages(updatedMessages);
                  }
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
        
        // Mark the assistant message as complete
        const completedAssistantMessage: ThreadMessage = {
          id: assistantMessageId,
          createdAt: new Date(),
          role: 'assistant',
          content: [{ type: 'text', text: accumulatedText }],
          status: { type: 'complete', reason: 'stop' },
          metadata: {
            unstable_state: undefined,
            unstable_annotations: undefined,
            unstable_data: undefined,
            steps: undefined,
            submittedFeedback: undefined,
            custom: {}
          }
        } as any;
        
        // Update the messages array with the completed message
        if (adapter.messages && adapter.setMessages) {
          const currentMessages = adapter.messages || [];
          const finalMessages = [...currentMessages.slice(0, -1), completedAssistantMessage];
          adapter.setMessages(finalMessages);
        }
      } finally {
        reader.releaseLock();
      }
    },
    onEdit: async () => {},
    onReload: async () => {},
    onAddToolResult: () => {},
    onResumeToolCall: () => {},
    adapters: {},
    isLoading: false,
  };

  return useExternalStoreRuntime(adapter);
};
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import json
import asyncio
from agent_service.agent import AgentService

app = FastAPI(
    title="A2A Agent Service API",
    description="AI Agent as a Service with streaming responses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent service
agent_service = AgentService()

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns 200 OK with status information
    """
    return {"status": "ok"}

@app.get("/a2a/models")
async def get_models():
    """
    Return list of available models
    """
    if agent_service.use_real_llm:
        # In a real implementation, this would fetch from the LLM provider
        return {"models": ["gpt-3.5-turbo", "gpt-4"]}
    else:
        # Return mock models when using mock responses
        return {"models": ["mock-model"]}

@app.delete("/a2a/conversations/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """
    Reset a specific conversation
    """
    agent_service.reset_conversation(conversation_id)
    return {"message": f"Conversation {conversation_id} reset successfully"}

@app.post("/a2a/messages")
async def handle_messages(
    request: Request,
    conversation_id: str = Query("default", description="Conversation ID to maintain context")
):
    """
    Main endpoint for handling chat messages
    Request: {"messages": [{"role": "user", "content": "string"}]}
    Response: SSE stream with token deltas
    """
    try:
        # Parse the request body
        body = await request.json()
        messages = body.get("messages", [])
        
        if not messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
        # Validate message format
        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise HTTPException(status_code=400, detail="Each message must have 'role' and 'content'")
        
        # Create a streaming response
        async def event_generator():
            try:
                # Process messages and stream the response
                async for chunk in agent_service.aprocess_messages(messages, conversation_id):
                    # Format as SSE: data: <content>\n\n
                    yield f"data: {chunk}\n\n"
                # Send a completion message to signal end of stream
                yield f"data: [DONE]\n\n"
            except Exception as e:
                # Send error as SSE data if something goes wrong during streaming
                yield f"data: Error occurred: {str(e)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Check if port is available
    def check_port(host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                s.close()
                return True
            except OSError:
                return False
    
    # Find an available port
    host = "0.0.0.0"
    port = 8000
    if not check_port(host, port):
        print(f"Port {port} is already in use. Please stop the existing server first.")
        print(f"Alternatively, run the server manually with: uvicorn server.main:app --host {host} --port {port}")
    else:
        uvicorn.run(app, host=host, port=port)
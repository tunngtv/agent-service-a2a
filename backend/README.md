# A2A Agent Service Backend

This is the backend component of the AI Chat application, providing an AI Agent as a Service with streaming responses via Server-Sent Events (SSE).

## Features

- FastAPI-based server
- LangChain-powered AI agent
- Streaming responses via SSE
- Health check endpoint
- Proper error handling

## API Endpoints

### GET /health
- Returns: `{"status": "ok"}`
- Purpose: Health check for the service

### POST /a2a/messages
- Request body: `{"messages": [{"role": "user", "content": "string"}]}`
- Response: SSE stream with token deltas
- Purpose: Process chat messages and stream AI responses

## Requirements

- Python 3.11+
- Poetry (for dependency management) or pip

## Installation

### Using Poetry (recommended)

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run the development server
poetry run dev
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional, will use mock responses if not set)

## Running in Production

```bash
# With Poetry
poetry run start

# With Uvicorn directly
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`
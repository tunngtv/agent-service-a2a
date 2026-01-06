# A2A Assistant UI

This is a Next.js application using the assistant-ui library to create a chat interface that connects to the A2A backend service.

## Installation

```bash
pnpm install
```

## Running the Application

```bash
# Make sure the A2A backend is running on port 8001
# Then run the frontend:
pnpm dev
```

The application will be available at `http://localhost:3000`

## Backend Integration

This application connects to the A2A backend service running at `http://localhost:8001`. The backend endpoint used is:

- POST `/a2a/messages` - for sending chat messages and receiving SSE responses

The `.env.local` file contains the configuration for the backend endpoint:

```
A2A_BASE_URL=http://localhost:8001
NEXT_PUBLIC_A2A_ENDPOINT=http://localhost:8001/a2a/messages
```

## Features

- Streaming chat responses from the A2A backend
- Stop generation functionality
- Reset chat functionality
- Full assistant-ui based chat interface

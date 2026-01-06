# AI Agent as a Service (A2A) - Full Stack Application

This is a complete full-stack AI Chat application with a backend A2A (Agent as a Service) server and a React frontend using @assistant-ui/react.

## Architecture

- **Backend**: FastAPI-based A2A server with LangChain agent
- **Frontend**: React + Vite + TailwindCSS with @assistant-ui/react
- **Streaming**: Server-Sent Events (SSE) for token streaming
- **Desktop**: Optional Electron wrapper

## Features

- Real-time streaming AI responses via SSE
- Clean separation of backend and frontend
- Full chat interface with message history
- Stop generation and reset functionality
- Cross-platform desktop application support

## Project Structure

```
agent_service_a2a/
├── backend/                 # FastAPI A2A server
│   ├── agent_service/       # LangChain agent implementation
│   └── server/              # FastAPI application
├── frontend/                # React/Vite frontend
│   └── apps/web/            # Web application
├── electron/                # Electron desktop wrapper
├── package.json             # Root package for Electron
└── README.md               # This file
```

## Installation & Setup

### Backend Setup

```bash
cd agent_service_a2a/backend

# Using pip
pip install -r requirements.txt

# Or using Poetry
poetry install
poetry shell
```

### Frontend Setup

```bash
cd agent_service_a2a/frontend

# Install dependencies
pnpm install

# If pnpm is not installed:
npm install -g pnpm
```

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# agent_service_a2a/backend/.env
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### Development Mode

```bash
cd agent_service_a2a

# Install root dependencies
npm install

# Run both backend and frontend concurrently
npm run dev
```

This will start:
- Backend API server on `http://localhost:8000`
- Frontend development server on `http://localhost:5173`

### Running Separately

**Backend only:**
```bash
cd agent_service_a2a/backend
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend only:**
```bash
cd agent_service_a2a/frontend/apps/web
pnpm dev
```

### Production Build

**Frontend:**
```bash
cd agent_service_a2a/frontend
pnpm build
```

**Run production backend:**
```bash
cd agent_service_a2a/backend
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

### Desktop Application

**Development:**
```bash
cd agent_service_a2a
npm run electron:dev
```

**Build for distribution:**
```bash
cd agent_service_a2a
npm run electron:dist
```

## API Endpoints

### Health Check
- `GET /health` - Returns service status

### Chat Messages
- `POST /a2a/messages` - Send chat messages and receive SSE stream
- Request body: `{ "messages": [{"role": "user", "content": "string"}] }`
- Response: SSE stream with token deltas

## Technologies Used

### Backend
- Python 3.11+
- FastAPI
- LangChain
- Uvicorn
- Server-Sent Events (SE)

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- @assistant-ui/react

### Desktop
- Electron
- electron-builder

## Project Status

✅ Backend A2A server with streaming responses  
✅ React frontend with @assistant-ui/react  
✅ SSE streaming implementation  
✅ Electron desktop wrapper  
✅ Complete project structure  
✅ Documentation and run instructions  

The application is fully functional with streaming AI responses from the backend to the frontend chat interface.
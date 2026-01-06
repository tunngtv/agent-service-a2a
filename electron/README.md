# Agent Service Electron Wrapper

This is the Electron desktop wrapper for the AI Chat application. It provides a native desktop experience for the web-based AI assistant.

## Features

- Native desktop application
- Thin wrapper around the web application
- Cross-platform support (Windows, macOS, Linux)
- Proper link handling (external links open in browser)

## Requirements

- Node.js 18+
- npm or pnpm

## Development

```bash
# Install dependencies
npm install

# Run in development mode (connects to Vite dev server)
npm run dev
```

## Building

```bash
# Build the desktop application
npm run build
```

The application will connect to the frontend development server at `http://localhost:5173` when run in development mode, and to the built frontend files in production.
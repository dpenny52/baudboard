# Baudboard

A kanban board application inspired by Linear, built with React + TypeScript and a Python FastAPI backend.

Built by a Lattice agent team 🤖

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, @dnd-kit, Zustand
- **Backend**: Python, FastAPI, SQLAlchemy (async), SQLite

## Getting Started

### Backend

```bash
cd backend
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to the backend at `localhost:8000`.

## Features

- Multiple boards with customizable columns
- Drag-and-drop cards between columns
- Card priorities (urgent, high, medium, low)
- Color-coded labels
- Card detail view with inline editing
- Dark theme (Linear-inspired)

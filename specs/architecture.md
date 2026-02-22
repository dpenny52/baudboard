# Baudboard Architecture

## Overview

Baudboard is a kanban board application inspired by Linear's kanban board UI. It features a clean, modern interface for managing tasks across customizable columns with drag-and-drop support.

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **@dnd-kit** for drag-and-drop
- **CSS Modules** for styling (no external UI framework — keep it lightweight)
- **Zustand** for state management
- **React Router** for navigation (future multi-board support)

### Backend
- **Python 3.12+** with **FastAPI**
- **SQLite** via **SQLAlchemy** (async) for persistence
- **Pydantic v2** for request/response models
- **Uvicorn** as ASGI server
- **Alembic** for database migrations

### Communication
- REST API for CRUD operations
- Server-Sent Events (SSE) for real-time updates (future)

## Data Model

### Board
- `id` (UUID)
- `name` (string)
- `created_at` (datetime)
- `updated_at` (datetime)

### Column (Status)
- `id` (UUID)
- `board_id` (FK → Board)
- `name` (string, e.g. "Backlog", "In Progress", "Done")
- `position` (integer, for ordering)
- `color` (string, hex color code)

### Card (Task)
- `id` (UUID)
- `board_id` (FK → Board)
- `column_id` (FK → Column)
- `title` (string)
- `description` (text, optional)
- `position` (integer, for ordering within column)
- `priority` (enum: none, low, medium, high, urgent)
- `labels` (JSON array of label objects)
- `created_at` (datetime)
- `updated_at` (datetime)

### Label
- `id` (UUID)
- `board_id` (FK → Board)
- `name` (string)
- `color` (string, hex color code)

## API Endpoints

### Boards
- `GET /api/boards` — list all boards
- `POST /api/boards` — create a board
- `GET /api/boards/{id}` — get board with columns and cards
- `PUT /api/boards/{id}` — update board
- `DELETE /api/boards/{id}` — delete board

### Columns
- `POST /api/boards/{board_id}/columns` — create column
- `PUT /api/columns/{id}` — update column (name, position, color)
- `DELETE /api/columns/{id}` — delete column
- `PUT /api/columns/reorder` — bulk reorder columns

### Cards
- `POST /api/boards/{board_id}/cards` — create card
- `GET /api/cards/{id}` — get card details
- `PUT /api/cards/{id}` — update card
- `DELETE /api/cards/{id}` — delete card
- `PUT /api/cards/{id}/move` — move card to different column/position
- `PUT /api/cards/reorder` — bulk reorder cards within a column

### Labels
- `GET /api/boards/{board_id}/labels` — list labels
- `POST /api/boards/{board_id}/labels` — create label
- `PUT /api/labels/{id}` — update label
- `DELETE /api/labels/{id}` — delete label

## Directory Structure

```
baudboard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── database.py          # SQLAlchemy async engine + session
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── boards.py
│   │   │   ├── columns.py
│   │   │   └── cards.py
│   │   └── seed.py              # Optional seed data
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   │   └── client.ts        # API client functions
│   │   ├── store/
│   │   │   └── boardStore.ts    # Zustand store
│   │   ├── components/
│   │   │   ├── Board.tsx
│   │   │   ├── Column.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── CardDetail.tsx
│   │   │   ├── CreateCardModal.tsx
│   │   │   └── Header.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── styles/
│   │       ├── global.css
│   │       ├── Board.module.css
│   │       ├── Column.module.css
│   │       └── Card.module.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── specs/                        # Project specs (this directory)
├── lattice.yaml                  # Lattice agent config
└── README.md
```

# Baudboard — Task Breakdown

Each task is a discrete, implementable unit with clear acceptance criteria. Tasks are ordered by dependency — complete them sequentially.

---

## Task 1: Project Scaffolding & Backend Foundation ✅ COMPLETED

**Goal**: Set up the project structure, backend framework, and database layer.

**Deliverables**:
1. Create `backend/` directory with a Python project:
   - `backend/pyproject.toml` with dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `aiosqlite`, `pydantic>=2.0`
   - `backend/requirements.txt` generated from pyproject.toml
2. Create `backend/app/main.py`:
   - FastAPI app with CORS middleware (allow all origins for dev)
   - Lifespan handler that creates DB tables on startup
   - Health check endpoint: `GET /api/health` → `{"status": "ok"}`
3. Create `backend/app/database.py`:
   - Async SQLAlchemy engine using `aiosqlite` with `sqlite+aiosqlite:///./baudboard.db`
   - Async session factory (`async_sessionmaker`)
   - `get_db` dependency for FastAPI
   - `create_tables` async function
4. Create `backend/app/models.py` — SQLAlchemy ORM models:
   - `Board`: id (UUID, PK), name (string, not null), created_at (datetime, server default), updated_at (datetime, on update)
   - `Column`: id (UUID, PK), board_id (FK → boards.id, cascade delete), name (string), position (integer), color (string, default "#6B7280")
   - `Card`: id (UUID, PK), board_id (FK → boards.id, cascade delete), column_id (FK → columns.id, cascade delete), title (string, not null), description (text, nullable), position (integer), priority (string, default "none"), labels (JSON, default []), created_at, updated_at
   - `Label`: id (UUID, PK), board_id (FK → boards.id, cascade delete), name (string), color (string)
5. Create `backend/app/schemas.py` — Pydantic v2 models:
   - Request models: `BoardCreate`, `BoardUpdate`, `ColumnCreate`, `ColumnUpdate`, `CardCreate`, `CardUpdate`, `CardMove`, `LabelCreate`, `LabelUpdate`
   - Response models: `BoardResponse`, `ColumnResponse`, `CardResponse`, `LabelResponse`, `BoardDetailResponse` (includes columns with cards)

**Acceptance Criteria**:
- `cd backend && pip install -e .` succeeds
- `uvicorn app.main:app` starts without errors
- `GET /api/health` returns 200 with `{"status": "ok"}`
- Database file is created on first startup with correct schema

---

## Task 2: Board & Column CRUD API

**Goal**: Implement REST endpoints for boards and columns.

**Deliverables**:
1. Create `backend/app/routers/boards.py`:
   - `POST /api/boards` — create board, auto-create default columns ("Backlog", "Todo", "In Progress", "Done") with positions 0-3 and distinct colors
   - `GET /api/boards` — list all boards (id, name, created_at only)
   - `GET /api/boards/{board_id}` — get board with all columns (ordered by position) and cards per column (ordered by position)
   - `PUT /api/boards/{board_id}` — update board name
   - `DELETE /api/boards/{board_id}` — delete board (cascades to columns and cards)
2. Create `backend/app/routers/columns.py`:
   - `POST /api/boards/{board_id}/columns` — create column (auto-assign position as max+1)
   - `PUT /api/columns/{column_id}` — update column name, color
   - `DELETE /api/columns/{column_id}` — delete column (move cards to first remaining column, or delete if last column)
   - `PUT /api/columns/reorder` — accept `{column_ids: [uuid, uuid, ...]}` and update positions to match array order
3. Register routers in `main.py`

**Acceptance Criteria**:
- Creating a board returns the board with 4 default columns
- `GET /api/boards/{id}` returns nested columns with cards
- Columns are always returned ordered by `position`
- Deleting a column redistributes its cards
- Reorder endpoint correctly updates all column positions atomically
- All endpoints return appropriate HTTP status codes (201 for creation, 404 for not found, etc.)

---

## Task 3: Card CRUD & Move API

**Goal**: Implement card management endpoints including cross-column moves.

**Deliverables**:
1. Create `backend/app/routers/cards.py`:
   - `POST /api/boards/{board_id}/cards` — create card in specified column_id (auto-assign position as max+1 in that column)
   - `GET /api/cards/{card_id}` — get single card with full details
   - `PUT /api/cards/{card_id}` — update card fields (title, description, priority, labels)
   - `DELETE /api/cards/{card_id}` — delete card, reorder remaining cards in the column to close the gap
   - `PUT /api/cards/{card_id}/move` — move card: accept `{column_id, position}`. Update the card's column and position. Shift other cards in both source and target columns to maintain contiguous positions.
2. Register router in `main.py`

**Acceptance Criteria**:
- Cards are created with auto-incrementing positions within their column
- Moving a card between columns correctly updates positions in both source and target columns
- Moving a card within the same column (reorder) works correctly
- Deleting a card closes the position gap (no holes in position sequence)
- Priority accepts values: "none", "low", "medium", "high", "urgent"
- Labels field accepts a JSON array of `{name, color}` objects

---

## Task 4: Label CRUD API

**Goal**: Implement label management for boards.

**Deliverables**:
1. Add label routes to `backend/app/routers/` (either new file or extend boards router):
   - `GET /api/boards/{board_id}/labels` — list all labels for a board
   - `POST /api/boards/{board_id}/labels` — create a label
   - `PUT /api/labels/{label_id}` — update label name/color
   - `DELETE /api/labels/{label_id}` — delete label
2. Register routes in `main.py`

**Acceptance Criteria**:
- Labels are scoped to boards
- CRUD operations work correctly
- Deleting a label does not affect cards (cards store label data inline as JSON)

---

## Task 5: Frontend Scaffolding & TypeScript Types

**Goal**: Set up the React + TypeScript frontend with Vite and define all types.

**Deliverables**:
1. Initialize frontend with Vite:
   - `frontend/package.json` with dependencies: `react`, `react-dom`, `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`, `zustand`
   - Dev dependencies: `typescript`, `@types/react`, `@types/react-dom`, `vite`, `@vitejs/plugin-react`
   - `frontend/vite.config.ts` with proxy: `/api` → `http://localhost:8000`
   - `frontend/tsconfig.json` with strict mode
   - `frontend/index.html` with root div
2. Create `frontend/src/types/index.ts`:
   - `Board`, `Column`, `Card`, `Label`, `Priority` types matching backend schemas
   - `BoardDetail` type (board with columns and cards)
3. Create `frontend/src/main.tsx` — React entry point
4. Create `frontend/src/App.tsx` — placeholder app component
5. Create `frontend/src/styles/global.css`:
   - CSS reset
   - Dark theme base styles (Linear-inspired: dark backgrounds `#1a1a2e`, `#16213e`, accent colors)
   - CSS custom properties for colors, spacing, border-radius
   - Font: system font stack

**Acceptance Criteria**:
- `cd frontend && npm install && npm run dev` starts the dev server
- App renders a placeholder page
- TypeScript compiles with no errors
- Vite proxy routes `/api/*` to backend
- Dark theme CSS variables are defined and applied to body

---

## Task 6: API Client & Zustand Store

**Goal**: Build the frontend data layer — API client functions and a Zustand store.

**Deliverables**:
1. Create `frontend/src/api/client.ts`:
   - Functions for all API endpoints using `fetch`:
     - `fetchBoard(id)`, `fetchBoards()`, `createBoard(name)`, `deleteBoard(id)`
     - `createColumn(boardId, data)`, `updateColumn(id, data)`, `deleteColumn(id)`, `reorderColumns(columnIds)`
     - `createCard(boardId, data)`, `updateCard(id, data)`, `deleteCard(id)`, `moveCard(id, columnId, position)`
     - `fetchLabels(boardId)`, `createLabel(boardId, data)`, `updateLabel(id, data)`, `deleteLabel(id)`
   - All functions throw on non-2xx responses with error message from body
   - Base URL from `import.meta.env.VITE_API_URL || ''` (empty for proxy)
2. Create `frontend/src/store/boardStore.ts`:
   - Zustand store with state:
     - `board: BoardDetail | null`
     - `boards: Board[]`
     - `isLoading: boolean`
     - `error: string | null`
   - Actions:
     - `loadBoard(id)` — fetch and set board
     - `loadBoards()` — fetch board list
     - `addCard(columnId, title, description?)` — create card via API, update local state
     - `moveCard(cardId, targetColumnId, targetPosition)` — optimistic update: move card in local state immediately, then call API. On failure, reload board.
     - `updateCard(cardId, updates)` — update card
     - `deleteCard(cardId)` — delete card
     - `addColumn(name)` — create column
     - `deleteColumn(columnId)` — delete column
     - `reorderColumns(columnIds)` — reorder

**Acceptance Criteria**:
- API client functions correctly call all backend endpoints
- Zustand store manages board state with loading/error states
- `moveCard` does optimistic updates (instant UI feedback)
- Store actions catch errors and set `error` state

---

## Task 7: Board Layout — Columns & Cards (Static)

**Goal**: Build the main board UI with columns and cards (no drag-and-drop yet).

**Deliverables**:
1. Create `frontend/src/components/Header.tsx`:
   - Top bar with board name, centered
   - Minimal styling (dark background, white text, 48px height)
2. Create `frontend/src/components/Board.tsx`:
   - Horizontal scrollable container for columns
   - Loads board on mount (using store's `loadBoard`)
   - Shows loading spinner or skeleton while loading
   - Shows error message if load fails
   - Renders columns in position order
3. Create `frontend/src/components/Column.tsx`:
   - Column header: name + card count + color indicator (dot or left border in column's color)
   - "+" button to add new card (opens inline input — no modal needed, just a text input that appears at the bottom of the column)
   - Scrollable card list
   - Each column has a subtle background distinct from the board background
4. Create `frontend/src/components/Card.tsx`:
   - Card title (truncated if long)
   - Priority indicator (colored icon or badge: urgent=red, high=orange, medium=yellow, low=blue, none=hidden)
   - Label chips (small colored pills with label name)
   - Subtle hover effect
   - Click handler (for future detail view)
5. Create CSS modules for each component:
   - `Board.module.css`, `Column.module.css`, `Card.module.css`
   - Linear-inspired styling: rounded corners, subtle shadows, clean spacing
6. Update `App.tsx` to render Header + Board
7. Create seed data: on first load, if no boards exist, create a "My Project" board with some sample cards

**Acceptance Criteria**:
- Board renders with columns side by side, horizontally scrollable
- Each column shows its cards in order
- Cards display title, priority, and labels
- "+" button in column creates a new card via inline input
- Visual style is clean and dark-themed (Linear-inspired)
- Responsive: columns don't collapse on narrow screens (horizontal scroll instead)

---

## Task 8: Drag-and-Drop with @dnd-kit

**Goal**: Add drag-and-drop to move cards between columns and reorder within columns.

**Deliverables**:
1. Update `Board.tsx`:
   - Wrap in `DndContext` from `@dnd-kit/core`
   - Handle `onDragStart`, `onDragOver`, `onDragEnd` events
   - Use `DragOverlay` for the dragged card preview
   - On drag end: call store's `moveCard` with target column and position
2. Update `Column.tsx`:
   - Wrap card list in `SortableContext` from `@dnd-kit/sortable`
   - Use `useDroppable` for the column as a drop target
   - Visual feedback when a card is being dragged over (highlight border or background change)
3. Update `Card.tsx`:
   - Use `useSortable` from `@dnd-kit/sortable`
   - Apply transform/transition styles from sortable
   - Reduce opacity when dragging
4. Collision detection: use `closestCorners` or `rectIntersection` strategy for cross-column drops

**Acceptance Criteria**:
- Cards can be dragged and dropped within the same column to reorder
- Cards can be dragged between columns
- Drag overlay shows a preview of the card being moved
- Drop targets are visually indicated
- Position is persisted to backend after drop
- Optimistic update: card moves instantly, reverts on API failure

---

## Task 9: Card Detail View

**Goal**: Add a detail panel/modal for viewing and editing card details.

**Deliverables**:
1. Create `frontend/src/components/CardDetail.tsx`:
   - Slide-over panel (right side) or modal that opens when clicking a card
   - Editable title (click to edit, save on blur or Enter)
   - Editable description (textarea, markdown-style — plain text is fine, no renderer needed)
   - Priority selector (dropdown or button group)
   - Label management: show current labels, add/remove labels from board's label set
   - Column indicator (which column the card is in) with ability to change
   - Created date display
   - Delete button with confirmation
2. Style with `CardDetail.module.css`:
   - Overlay/backdrop behind the panel
   - Smooth slide-in animation
   - Clean form layout

**Acceptance Criteria**:
- Clicking a card opens the detail view
- All fields are editable and persist to backend on change
- Pressing Escape or clicking backdrop closes the panel
- Delete requires confirmation (simple "Are you sure?" prompt)
- Changes are reflected immediately in the board view

---

## Task 10: Board Management & Polish

**Goal**: Add board listing, creation, and UI polish.

**Deliverables**:
1. Create a board list view (`frontend/src/components/BoardList.tsx`):
   - Shows all boards as cards/tiles
   - "New Board" button with name input
   - Click board to navigate to it
2. Add routing:
   - `/` → Board list
   - `/board/:id` → Board view
   - Install and configure `react-router-dom`
3. Create `frontend/src/components/CreateCardModal.tsx` (enhance the inline input from Task 7):
   - Allow setting title, description, priority, and labels on creation
   - Can be triggered from column "+" button
4. Polish:
   - Empty state for columns (friendly "No cards yet" message)
   - Empty state for board list
   - Loading skeletons for board and card list
   - Keyboard shortcuts: Escape to close modals/detail panel, N to create new card
5. Update `README.md` at project root:
   - Project description
   - How to run (backend + frontend instructions)
   - Screenshot placeholder
   - Tech stack summary

**Acceptance Criteria**:
- Users can create, view, and navigate between multiple boards
- Board list shows all boards with creation option
- URL routing works (direct link to `/board/:id` loads correctly)
- Empty states are handled gracefully
- README has clear setup/run instructions
- App feels polished and responsive

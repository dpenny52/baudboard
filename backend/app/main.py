from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import boards, columns, labels


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    await create_tables()
    yield
    # Shutdown (can be empty for now)


app = FastAPI(
    title="Baudboard API",
    version="0.1.0",
    description="A kanban board application API",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(labels.router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

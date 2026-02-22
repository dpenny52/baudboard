from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Request Models
class BoardCreate(BaseModel):
    """Request model for creating a board."""

    name: str


class BoardUpdate(BaseModel):
    """Request model for updating a board."""

    name: str


class ColumnCreate(BaseModel):
    """Request model for creating a column."""

    name: str
    color: str | None = None


class ColumnUpdate(BaseModel):
    """Request model for updating a column."""

    name: str
    color: str


class CardCreate(BaseModel):
    """Request model for creating a card."""

    column_id: UUID
    title: str
    description: str | None = None


class CardUpdate(BaseModel):
    """Request model for updating a card."""

    title: str | None = None
    description: str | None = None
    priority: str
    labels: list


class CardMove(BaseModel):
    """Request model for moving a card."""

    column_id: UUID
    position: int


class LabelCreate(BaseModel):
    """Request model for creating a label."""

    name: str
    color: str


class LabelUpdate(BaseModel):
    """Request model for updating a label."""

    name: str
    color: str


# Response Models
class LabelResponse(BaseModel):
    """Response model for a label."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    color: str


class CardResponse(BaseModel):
    """Response model for a card."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    board_id: UUID
    column_id: UUID
    title: str
    description: str | None
    position: int
    priority: str
    labels: list
    created_at: datetime
    updated_at: datetime


class ColumnResponse(BaseModel):
    """Response model for a column."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    board_id: UUID
    name: str
    position: int
    color: str
    cards: list[CardResponse] = []


class BoardResponse(BaseModel):
    """Response model for a board."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime


class BoardDetailResponse(BaseModel):
    """Detailed response model for a board with all columns and cards."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    columns: list[ColumnResponse] = []

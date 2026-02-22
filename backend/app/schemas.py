from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    name: str | None = None
    color: str | None = None


class ColumnReorder(BaseModel):
    """Request model for reordering columns."""

    column_ids: list[str]


class CardCreate(BaseModel):
    """Request model for creating a card."""

    column_id: str
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

    column_id: str
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

    id: str = Field(serialization_alias="id")
    name: str
    color: str


class CardResponse(BaseModel):
    """Response model for a card."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(serialization_alias="id")
    board_id: str
    column_id: str
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

    id: str = Field(serialization_alias="id")
    board_id: str
    name: str
    position: int
    color: str
    cards: list[CardResponse] = []


class BoardResponse(BaseModel):
    """Response model for a board."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(serialization_alias="id")
    name: str
    created_at: datetime


class BoardDetailResponse(BaseModel):
    """Detailed response model for a board with all columns and cards."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(serialization_alias="id")
    name: str
    created_at: datetime
    updated_at: datetime
    columns: list[ColumnResponse] = []

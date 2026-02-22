from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Board, Column, Card
from app.schemas import (
    BoardCreate,
    BoardUpdate,
    BoardResponse,
    BoardDetailResponse,
    ColumnResponse,
    CardResponse,
)

router = APIRouter(prefix="/api/boards", tags=["boards"])

# Default columns configuration
DEFAULT_COLUMNS = [
    {"name": "Backlog", "color": "#6B7280", "position": 0},
    {"name": "Todo", "color": "#3B82F6", "position": 1},
    {"name": "In Progress", "color": "#F59E0B", "position": 2},
    {"name": "Done", "color": "#10B981", "position": 3},
]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BoardDetailResponse)
async def create_board(
    board_data: BoardCreate,
    db: AsyncSession = Depends(get_db),
) -> BoardDetailResponse:
    """Create a new board with 4 default columns."""
    # Create the board
    board = Board(name=board_data.name)
    db.add(board)
    await db.flush()  # Flush to get the board ID

    # Create default columns
    columns = []
    for col_spec in DEFAULT_COLUMNS:
        column = Column(
            board_id=board.id,
            name=col_spec["name"],
            color=col_spec["color"],
            position=col_spec["position"],
        )
        db.add(column)
        columns.append(column)

    await db.commit()
    await db.refresh(board)

    # Build response
    return BoardDetailResponse(
        id=board.id,
        name=board.name,
        created_at=board.created_at,
        updated_at=board.updated_at,
        columns=[
            ColumnResponse(
                id=col.id,
                board_id=col.board_id,
                name=col.name,
                position=col.position,
                color=col.color,
                cards=[],
            )
            for col in columns
        ],
    )


@router.get("", response_model=list[BoardResponse])
async def list_boards(
    db: AsyncSession = Depends(get_db),
) -> list[BoardResponse]:
    """List all boards."""
    result = await db.execute(select(Board).order_by(Board.created_at))
    boards = result.scalars().all()
    return [
        BoardResponse(
            id=b.id,
            name=b.name,
            created_at=b.created_at,
        )
        for b in boards
    ]


@router.get("/{board_id}", response_model=BoardDetailResponse)
async def get_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> BoardDetailResponse:
    """Get a single board with all its columns and cards."""
    # Convert UUID to string for database query
    board_id_str = str(board_id)

    # Fetch board with columns and cards eagerly loaded
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id_str)
        .options(
            selectinload(Board.columns).selectinload(Column.cards)
        )
    )
    board = result.unique().scalar_one_or_none()

    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    # Sort columns by position
    sorted_columns = sorted(board.columns, key=lambda c: c.position)

    # Build the response
    columns_response = [
        ColumnResponse(
            id=col.id,
            board_id=col.board_id,
            name=col.name,
            position=col.position,
            color=col.color,
            cards=[
                CardResponse(
                    id=card.id,
                    board_id=card.board_id,
                    column_id=card.column_id,
                    title=card.title,
                    description=card.description,
                    position=card.position,
                    priority=card.priority,
                    labels=card.labels or [],
                    created_at=card.created_at,
                    updated_at=card.updated_at,
                )
                for card in sorted(col.cards, key=lambda c: c.position)
            ],
        )
        for col in sorted_columns
    ]

    return BoardDetailResponse(
        id=board.id,
        name=board.name,
        created_at=board.created_at,
        updated_at=board.updated_at,
        columns=columns_response,
    )


@router.put("/{board_id}", response_model=BoardDetailResponse)
async def update_board(
    board_id: UUID,
    board_data: BoardUpdate,
    db: AsyncSession = Depends(get_db),
) -> BoardDetailResponse:
    """Update board name."""
    # Convert UUID to string for database query
    board_id_str = str(board_id)

    # Fetch board with columns and cards
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id_str)
        .options(
            selectinload(Board.columns).selectinload(Column.cards)
        )
    )
    board = result.unique().scalar_one_or_none()

    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    # Update the board name
    board.name = board_data.name
    await db.commit()
    await db.refresh(board)

    # Sort columns by position
    sorted_columns = sorted(board.columns, key=lambda c: c.position)

    # Build the response
    columns_response = [
        ColumnResponse(
            id=col.id,
            board_id=col.board_id,
            name=col.name,
            position=col.position,
            color=col.color,
            cards=[
                CardResponse(
                    id=card.id,
                    board_id=card.board_id,
                    column_id=card.column_id,
                    title=card.title,
                    description=card.description,
                    position=card.position,
                    priority=card.priority,
                    labels=card.labels or [],
                    created_at=card.created_at,
                    updated_at=card.updated_at,
                )
                for card in sorted(col.cards, key=lambda c: c.position)
            ],
        )
        for col in sorted_columns
    ]

    return BoardDetailResponse(
        id=board.id,
        name=board.name,
        created_at=board.created_at,
        updated_at=board.updated_at,
        columns=columns_response,
    )


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a board and cascade delete all its columns and cards."""
    # Convert UUID to string for database query
    board_id_str = str(board_id)

    result = await db.execute(select(Board).where(Board.id == board_id_str))
    board = result.scalar_one_or_none()

    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    await db.delete(board)
    await db.commit()

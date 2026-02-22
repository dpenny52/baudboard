from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Board, Column, Card
from app.schemas import (
    ColumnCreate,
    ColumnUpdate,
    ColumnResponse,
    ColumnReorder,
    CardResponse,
)

router = APIRouter(prefix="/api", tags=["columns"])


@router.post(
    "/boards/{board_id}/columns",
    status_code=status.HTTP_201_CREATED,
    response_model=ColumnResponse,
)
async def create_column(
    board_id: UUID,
    column_data: ColumnCreate,
    db: AsyncSession = Depends(get_db),
) -> ColumnResponse:
    """Create a new column in a board."""
    # Convert UUID to string for database query
    board_id_str = str(board_id)

    # Check if board exists
    board_result = await db.execute(select(Board).where(Board.id == board_id_str))
    board = board_result.scalar_one_or_none()

    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    # Get the max position for existing columns
    position_result = await db.execute(
        select(Column.position).where(Column.board_id == board_id_str)
    )
    positions = position_result.scalars().all()
    new_position = max(positions) + 1 if positions else 0

    # Create the column
    column = Column(
        board_id=board_id_str,
        name=column_data.name,
        color=column_data.color or "#6B7280",  # Default color if not provided
        position=new_position,
    )
    db.add(column)
    await db.commit()
    await db.refresh(column)

    return ColumnResponse(
        id=column.id,
        board_id=column.board_id,
        name=column.name,
        position=column.position,
        color=column.color,
        cards=[],
    )


@router.put(
    "/columns/{column_id}",
    response_model=ColumnResponse,
)
async def update_column(
    column_id: UUID,
    column_data: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
) -> ColumnResponse:
    """Update column name and/or color."""
    # Convert UUID to string for database query
    column_id_str = str(column_id)

    result = await db.execute(
        select(Column)
        .where(Column.id == column_id_str)
        .options(selectinload(Column.cards))
    )
    column = result.unique().scalar_one_or_none()

    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found",
        )

    # Update fields if provided
    if column_data.name is not None:
        column.name = column_data.name
    if column_data.color is not None:
        column.color = column_data.color

    await db.commit()
    await db.refresh(column)

    # Build response
    cards_response = [
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
        for card in sorted(column.cards, key=lambda c: c.position)
    ]

    return ColumnResponse(
        id=column.id,
        board_id=column.board_id,
        name=column.name,
        position=column.position,
        color=column.color,
        cards=cards_response,
    )


@router.delete(
    "/columns/{column_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_column(
    column_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a column.
    If not the last column in the board, move all its cards to the first remaining column.
    If it's the last column, delete all its cards too.
    Update positions of remaining cards to close gaps.
    """
    # Convert UUID to string for database query
    column_id_str = str(column_id)

    # Fetch the column with its cards and the board info
    column_result = await db.execute(
        select(Column)
        .where(Column.id == column_id_str)
        .options(selectinload(Column.cards))
    )
    column = column_result.unique().scalar_one_or_none()

    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found",
        )

    board_id = column.board_id

    # Get all columns in the board
    board_result = await db.execute(
        select(Column).where(Column.board_id == board_id)
    )
    all_columns = board_result.scalars().all()

    # Check if this is the last column
    is_last_column = len(all_columns) == 1

    if is_last_column:
        # Delete all cards in this column
        for card in column.cards:
            await db.delete(card)
    else:
        # Move cards to the first remaining column
        # Find the first column by position (excluding this one)
        remaining_columns = [c for c in all_columns if c.id != column_id_str]
        target_column = min(remaining_columns, key=lambda c: c.position)

        # Get max position in target column
        max_position_result = await db.execute(
            select(Card.position).where(Card.column_id == target_column.id)
        )
        positions = max_position_result.scalars().all()
        next_position = max(positions) + 1 if positions else 0

        # Move all cards from this column to target column
        for idx, card in enumerate(column.cards):
            card.column_id = target_column.id
            card.position = next_position + idx

    # Delete the column
    await db.delete(column)
    await db.commit()


@router.put(
    "/columns/reorder",
    response_model=list[ColumnResponse],
)
async def reorder_columns(
    reorder_data: ColumnReorder,
    db: AsyncSession = Depends(get_db),
) -> list[ColumnResponse]:
    """
    Bulk reorder columns.
    All columns must belong to the same board.
    Update the position of each column to match its index in the array.
    """
    if not reorder_data.column_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="column_ids list cannot be empty",
        )

    # Column IDs are already strings
    column_ids = reorder_data.column_ids

    # Fetch all specified columns
    columns_result = await db.execute(
        select(Column).where(Column.id.in_(column_ids))
    )
    columns = {col.id: col for col in columns_result.scalars().all()}

    # Validate all columns exist
    if len(columns) != len(column_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more columns not found",
        )

    # Check all columns belong to the same board
    board_ids = {col.board_id for col in columns.values()}
    if len(board_ids) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All columns must belong to the same board",
        )

    # Update positions
    updated_columns = []
    for position, column_id in enumerate(column_ids):
        col = columns[column_id]
        col.position = position
        updated_columns.append(col)

    await db.commit()

    # Sort by new position for response
    updated_columns.sort(key=lambda c: c.position)

    # Build response
    return [
        ColumnResponse(
            id=col.id,
            board_id=col.board_id,
            name=col.name,
            position=col.position,
            color=col.color,
            cards=[],
        )
        for col in updated_columns
    ]

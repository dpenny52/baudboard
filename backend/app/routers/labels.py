from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Board, Label
from app.schemas import LabelCreate, LabelResponse, LabelUpdate

router = APIRouter()


@router.get("/api/boards/{board_id}/labels", response_model=List[LabelResponse])
async def get_labels(
    board_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[Label]:
    """Get all labels for a board."""
    # Verify board exists
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    # Get all labels for the board
    result = await db.execute(
        select(Label)
        .where(Label.board_id == board_id)
        .order_by(Label.name)
    )
    labels = result.scalars().all()
    return list(labels)


@router.post(
    "/api/boards/{board_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_label(
    board_id: str,
    label_data: LabelCreate,
    db: AsyncSession = Depends(get_db),
) -> Label:
    """Create a new label for a board."""
    # Verify board exists
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )

    # Check if a label with the same name already exists in this board
    result = await db.execute(
        select(Label).where(
            Label.board_id == board_id,
            Label.name == label_data.name,
        )
    )
    existing_label = result.scalar_one_or_none()
    if existing_label:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Label with name '{label_data.name}' already exists in this board",
        )

    # Create the label
    new_label = Label(
        board_id=board_id,
        name=label_data.name,
        color=label_data.color,
    )
    db.add(new_label)
    await db.commit()
    await db.refresh(new_label)

    return new_label


@router.put("/api/labels/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: str,
    label_data: LabelUpdate,
    db: AsyncSession = Depends(get_db),
) -> Label:
    """Update a label."""
    # Get the label
    result = await db.execute(select(Label).where(Label.id == label_id))
    label = result.scalar_one_or_none()
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    # If updating the name, check for duplicates
    if label_data.name is not None and label_data.name != label.name:
        result = await db.execute(
            select(Label).where(
                Label.board_id == label.board_id,
                Label.name == label_data.name,
            )
        )
        existing_label = result.scalar_one_or_none()
        if existing_label:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Label with name '{label_data.name}' already exists in this board",
            )

    # Update fields
    update_data = label_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(label, field, value)

    await db.commit()
    await db.refresh(label)

    return label


@router.delete("/api/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a label."""
    # Get the label
    result = await db.execute(select(Label).where(Label.id == label_id))
    label = result.scalar_one_or_none()
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    # Delete the label
    await db.delete(label)
    await db.commit()

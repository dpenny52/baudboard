from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Card, Column
from app.schemas import CardCreate, CardUpdate, CardMove, CardResponse

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CardResponse)
async def create_card(
    card_data: CardCreate,
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """Create a new card in a column."""
    # Convert UUID to string for database query
    column_id_str = str(card_data.column_id)
    
    # Check if column exists
    result = await db.execute(select(Column).where(Column.id == column_id_str))
    column = result.scalar_one_or_none()
    
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Column not found",
        )
    
    # Get the current max position in the column
    result = await db.execute(
        select(Card)
        .where(Card.column_id == column_id_str)
        .order_by(Card.position.desc())
    )
    cards = result.scalars().all()
    max_position = cards[0].position if cards else -1
    
    # Create the card
    card = Card(
        board_id=column.board_id,
        column_id=column_id_str,
        title=card_data.title,
        description=card_data.description,
        position=max_position + 1,
        priority=card_data.priority or "none",
        labels=card_data.labels or [],
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return CardResponse(
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


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """Get a single card by ID."""
    # Convert UUID to string for database query
    card_id_str = str(card_id)
    
    result = await db.execute(select(Card).where(Card.id == card_id_str))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    return CardResponse(
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


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: UUID,
    card_data: CardUpdate,
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """Update a card's details (title, description, priority, labels)."""
    # Convert UUID to string for database query
    card_id_str = str(card_id)
    
    result = await db.execute(select(Card).where(Card.id == card_id_str))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    # Update fields if provided
    if card_data.title is not None:
        card.title = card_data.title
    if card_data.description is not None:
        card.description = card_data.description
    if card_data.priority is not None:
        card.priority = card_data.priority
    if card_data.labels is not None:
        card.labels = card_data.labels
    
    await db.commit()
    await db.refresh(card)
    
    return CardResponse(
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


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a card."""
    # Convert UUID to string for database query
    card_id_str = str(card_id)
    
    result = await db.execute(select(Card).where(Card.id == card_id_str))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    # Store the column_id and position before deleting
    column_id = card.column_id
    deleted_position = card.position
    
    # Delete the card
    await db.delete(card)
    
    # Reposition remaining cards in the column
    result = await db.execute(
        select(Card)
        .where(Card.column_id == column_id)
        .where(Card.position > deleted_position)
        .order_by(Card.position)
    )
    cards_to_update = result.scalars().all()
    
    for card in cards_to_update:
        card.position -= 1
    
    await db.commit()


@router.post("/{card_id}/move", response_model=CardResponse)
async def move_card(
    card_id: UUID,
    move_data: CardMove,
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """Move a card to a different column and/or position."""
    # Convert UUIDs to strings for database queries
    card_id_str = str(card_id)
    new_column_id_str = str(move_data.column_id)
    
    # Fetch the card
    result = await db.execute(select(Card).where(Card.id == card_id_str))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    # Check if the new column exists
    result = await db.execute(select(Column).where(Column.id == new_column_id_str))
    new_column = result.scalar_one_or_none()
    
    if not new_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target column not found",
        )
    
    # Store old position and column
    old_column_id = card.column_id
    old_position = card.position
    new_position = move_data.position
    
    # Moving within the same column
    if old_column_id == new_column_id_str:
        if old_position == new_position:
            # No change needed
            return CardResponse(
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
        
        # Get all cards in the column
        result = await db.execute(
            select(Card)
            .where(Card.column_id == old_column_id)
            .where(Card.id != card_id_str)
            .order_by(Card.position)
        )
        other_cards = result.scalars().all()
        
        # Update positions
        if new_position < old_position:
            # Moving up: shift cards down between new_position and old_position
            for other_card in other_cards:
                if new_position <= other_card.position < old_position:
                    other_card.position += 1
        else:
            # Moving down: shift cards up between old_position and new_position
            for other_card in other_cards:
                if old_position < other_card.position <= new_position:
                    other_card.position -= 1
        
        # Update the card's position
        card.position = new_position
    
    # Moving to a different column
    else:
        # Update positions in the old column (shift cards up)
        result = await db.execute(
            select(Card)
            .where(Card.column_id == old_column_id)
            .where(Card.position > old_position)
            .order_by(Card.position)
        )
        old_column_cards = result.scalars().all()
        
        for other_card in old_column_cards:
            other_card.position -= 1
        
        # Update positions in the new column (shift cards down)
        result = await db.execute(
            select(Card)
            .where(Card.column_id == new_column_id_str)
            .where(Card.position >= new_position)
            .order_by(Card.position)
        )
        new_column_cards = result.scalars().all()
        
        for other_card in new_column_cards:
            other_card.position += 1
        
        # Update the card's column and position
        card.column_id = new_column_id_str
        card.position = new_position
    
    # Commit all changes
    await db.commit()
    await db.refresh(card)
    
    return CardResponse(
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

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, insert, func
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "none"
    labels: List[dict] = []

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[dict]] = None

class CardResponse(CardCreate):
    id: int
    column_id: int
    position: int

# Dependency to get the DB session
async def get_db_session() -> AsyncSession:
    # Implementation for getting session
    pass

@router.post("/api/boards/{board_id}/cards", response_model=CardResponse)
async def create_card(board_id: int, column_id: int, card: CardCreate, db: AsyncSession = Depends(get_db_session)):
    # Get max position in the specified column
    result = await db.execute(select(func.max(Card.position)).where(Card.column_id == column_id))
    max_position = result.scalar() or 0
    new_position = max_position + 1
    # Insert card
    new_card = Card(**card.dict(), column_id=column_id, position=new_position)
    db.add(new_card)
    await db.commit()
    await db.refresh(new_card)
    return new_card

@router.get("/api/cards/{card_id}", response_model=CardResponse)
async def get_card(card_id: int, db: AsyncSession = Depends(get_db_session)):
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.put("/api/cards/{card_id}", response_model=CardResponse)
async def update_card(card_id: int, card_data: CardUpdate, db: AsyncSession = Depends(get_db_session)):
    query = update(Card).where(Card.id == card_id).values(card_data.dict(exclude_unset=True))
    await db.execute(query)
    await db.commit()  
    updated_card = await db.get(Card, card_id)
    return updated_card

@router.delete("/api/cards/{card_id}")
async def delete_card(card_id: int, db: AsyncSession = Depends(get_db_session)):
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    # Delete card
await db.delete(card)
    await db.commit()
    # Reorder remaining cards
    await db.execute(
        update(Card)
        .where(Card.column_id == card.column_id)
        .where(Card.position > card.position)
        .values(position=Card.position - 1)
    )

@router.put("/api/cards/{card_id}/move")
async def move_card(card_id: int, column_id: int, position: int, db: AsyncSession = Depends(get_db_session)):
    # Retrieve card to move
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    # Update positions of cards if moving to a different column
    if card.column_id != column_id:
        # Shift cards in target column
        await db.execute(
            update(Card)
            .where(Card.column_id == column_id)
            .where(Card.position >= position)
            .values(position=Card.position + 1)
        )
    # Move card
    card.column_id = column_id
    card.position = position
    await db.commit()
    return card

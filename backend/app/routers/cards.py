from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models import Card, Column
from app.database import db  # Adjust import depending on your DB session management

router = APIRouter()

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str  # Can be 'none', 'low', 'medium', 'high', 'urgent'
    labels: List[dict]  # List of {'name': str, 'color': str}

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[dict]] = None

@router.post("/api/boards/{board_id}/cards", response_model=Card)
async def create_card(board_id: int, column_id: int, card: CardCreate):
    async with db.transaction():
        max_position = await db.fetchval("SELECT MAX(position) FROM cards WHERE column_id = ?", column_id)
        position = (max_position or 0) + 1
        new_card = await db.execute("INSERT INTO cards (title, description, priority, labels, column_id, position) VALUES (?, ?, ?, ?, ?, ?) RETURNING *", (card.title, card.description, card.priority, card.labels, column_id, position))
        return new_card

@router.get("/api/cards/{card_id}", response_model=Card)
async def get_card(card_id: int):
    card = await db.fetchrow("SELECT * FROM cards WHERE id = ?", card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.put("/api/cards/{card_id}")
async def update_card(card_id: int, card_update: CardUpdate):
    updated_fields = card_update.dict(exclude_unset=True)
    if not updated_fields:
        raise HTTPException(detail="No fields to update", status_code=400)
    set_clause = ", ".join([f"{key} = ?" for key in updated_fields])
    values = list(updated_fields.values()) + [card_id]
    await db.execute(f"UPDATE cards SET {set_clause} WHERE id = ?", values)
    return {"status": "success"}

@router.delete("/api/cards/{card_id}")
async def delete_card(card_id: int):
    async with db.transaction():
        await db.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        # Close gap in positions
        await db.execute("UPDATE cards SET position = position - 1 WHERE position > (SELECT position FROM cards WHERE id = ?)\n        AND column_id = (SELECT column_id FROM cards WHERE id = ?)", (card_id, card_id))
    return {"status": "deleted"}

@router.put("/api/cards/{card_id}/move")
async def move_card(card_id: int, column_id: int, position: int):
    async with db.transaction():
        old_column_id = await db.fetchval("SELECT column_id FROM cards WHERE id = ?", card_id)
        await db.execute("UPDATE cards SET column_id = ?, position = ? WHERE id = ?", (column_id, position, card_id))
        # Reorder cards in old column
        await db.execute("UPDATE cards SET position = position - 1 WHERE position > (SELECT position FROM cards WHERE id = ?) AND column_id = ?", (card_id, old_column_id))
        # Reorder cards in new column
        await db.execute("UPDATE cards SET position = position + 1 WHERE position >= ? AND column_id = ?", (position, column_id))
    return {"status": "moved"}
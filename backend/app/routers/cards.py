from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Card, Column, Board
from database import get_session
from uuid import UUID
from pydantic import BaseModel, constr
from typing import List, Optional

router = APIRouter()

class Label(BaseModel):
    name: str
    color: str

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: constr(regex='^(none|low|medium|high|urgent)$') = 'none'
    labels: List[Label] = []

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[constr(regex='^(none|low|medium|high|urgent)$')] = None
    labels: Optional[List[Label]] = None

@router.post('/api/boards/{board_id}/cards', response_model=Card)
async def create_card(board_id: UUID, column_id: UUID, card: CardCreate, session: AsyncSession = Depends(get_session)):
    # Auto-assign position
    result = await session.execute(select(Card).filter(Card.column_id == column_id).order_by(Card.position.desc()))
    max_position = result.scalars().first().position if result else 0
    new_card = Card(
        board_id=board_id,
        column_id=column_id,
        title=card.title,
        description=card.description,
        priority=card.priority,
        labels=card.labels,
        position=max_position + 1
    )
    session.add(new_card)
    await session.commit()
    return new_card

@router.get('/api/cards/{card_id}', response_model=Card)
async def get_card(card_id: UUID, session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail='Card not found')
    return card

@router.put('/api/cards/{card_id}', response_model=Card)
async def update_card(card_id: UUID, card_updates: CardUpdate, session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail='Card not found')

    for attr, value in card_updates.dict(exclude_unset=True).items():
        setattr(card, attr, value)
    await session.commit()
    return card

@router.delete('/api/cards/{card_id}')
async def delete_card(card_id: UUID, session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail='Card not found')
    column_id = card.column_id
    await session.delete(card)
    # Reorder cards in the column
    remaining_cards = await session.execute(select(Card).filter(Card.column_id == column_id).order_by(Card.position))
    for i, remaining_card in enumerate(remaining_cards.scalars()):
        remaining_card.position = i + 1
    await session.commit()

@router.put('/api/cards/{card_id}/move')
async def move_card(card_id: UUID, column_id: UUID, position: int, session: AsyncSession = Depends(get_session)):
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail='Card not found')

    original_column_id = card.column_id
    card.column_id = column_id
    card.position = position

    # Update positions in original and target columns
    # (omitted for brevity)  
    await session.commit()
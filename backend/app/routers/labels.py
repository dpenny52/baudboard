from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Label, Board
from app.dependencies import get_db
from app.schemas import LabelCreate, LabelUpdate

router = APIRouter()

@router.get("/api/boards/{board_id}/labels", response_model=List[Label])
async def list_labels(board_id: str, db: AsyncSession = Depends(get_db)):
    board = await db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    result = await db.execute(select(Label).where(Label.board_id == board_id))
    return result.scalars().all()

@router.post("/api/boards/{board_id}/labels", response_model=Label)
async def create_label(board_id: str, new_label: LabelCreate, db: AsyncSession = Depends(get_db)):
    board = await db.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    label = Label(**new_label.dict(), board_id=board_id)
    db.add(label)
    await db.commit()
    return label

@router.put("/api/labels/{label_id}", response_model=Label)
async def update_label(label_id: str, updated_label: LabelUpdate, db: AsyncSession = Depends(get_db)):
    label = await db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    for key, value in updated_label.dict(exclude_unset=True).items():
        setattr(label, key, value)
    await db.commit()
    return label

@router.delete("/api/labels/{label_id}")
async def delete_label(label_id: str, db: AsyncSession = Depends(get_db)):
    label = await db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    await db.delete(label)
    await db.commit()
    return {"detail": "Label deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

router = APIRouter()

class LabelBase(BaseModel):
    name: str
    color: str

class LabelCreate(LabelBase):
    pass

class LabelResponse(LabelBase):
    id: int
    board_id: int

# Dependency to get the DB session
async def get_db_session() -> AsyncSession:
    # Implementation for getting session
    pass

@router.get("/api/boards/{board_id}/labels", response_model=List[LabelResponse])
async def list_labels(board_id: int, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(Label).where(Label.board_id == board_id))
    return result.scalars().all()

@router.post("/api/boards/{board_id}/labels", response_model=LabelResponse)
async def create_label(board_id: int, label: LabelCreate, db: AsyncSession = Depends(get_db_session)):
    new_label = Label(**label.dict(), board_id=board_id)
    db.add(new_label)
    await db.commit()
    await db.refresh(new_label)
    return new_label

@router.put("/api/labels/{label_id}", response_model=LabelResponse)
async def update_label(label_id: int, label_data: LabelBase, db: AsyncSession = Depends(get_db_session)):
    query = update(Label).where(Label.id == label_id).values(label_data.dict())
    await db.execute(query)
    await db.commit()
    return await db.get(Label, label_id)

@router.delete("/api/labels/{label_id}")
async def delete_label(label_id: int, db: AsyncSession = Depends(get_db_session)):
    label = await db.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    await db.delete(label)
    await db.commit()
    return {"deleted": True}
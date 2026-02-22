from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.models import User
from app.security import create_access_token, get_password_hash, verify_password

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/api/users/register")
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_db_session)):
    # Check if the user already exists
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/api/users/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db_session)):
    db_user = await db.execute(select(User).where(User.username == user.username))
    db_user = db_user.scalars().first()
    if db_user is None or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(data={'sub': db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
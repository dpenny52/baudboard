from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.database import get_db_session
from app.models import User
from app.security import create_access_token

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/api/users/register")
async def register(user: UserRegister, db: AsyncSession = Depends(get_db_session)):
    # Check if the username or email already exists
    existing_user = await db.execute(select(User).filter((User.email == user.email) | (User.username == user.username)))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Email or Username already in use")
    # Create new user
    new_user = User(**user.dict())
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully"}

@router.post("/api/users/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db_session)):
    # Validate user credentials
    user_record = await db.execute(select(User).filter(User.email == user.email))
    user = user_record.scalars().first()
    if not user or not user.verify_password(user.password):  # Assuming a method verify_password in User model
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generate JWT token
    token = create_access_token(data={
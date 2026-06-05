from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select   
from app.db.db import AsyncSession, get_db
from app.models.auth import User
from app.schemas.auth import UserResponse , Token , UserLogin , UserRegister
from app.core.security import hash_password, verify_password, create_access_token
from app.api.dependency import get_current_user



router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalar_one_or_none()
    if existing_user: 
        raise HTTPException( status_code=400, detail="Email already registered" ) 
    user = User(name=payload.name,email=payload.email, hashed_password=hash_password(payload.password)) 
    db.add(user) 
    await db.commit() 
    await db.refresh(user) 
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me",response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
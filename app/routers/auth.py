from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.database import db

router = APIRouter(prefix="/auth", tags=["Registration"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    user = await db.create_user(
        telegram_id=user_data.telegram_id,
        name=user_data.name,
        username=user_data.username
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this telegram_id already exists"
        )
    
    return UserResponse(**user)
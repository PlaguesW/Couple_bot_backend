from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.user import UserResponse
from app.database import db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """Get all registered users"""
    users = await db.get_all_users()
    return [UserResponse(**user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(**user)
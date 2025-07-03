from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas import UserCreate, User, UsersListResponse, UserResponse
from app.crud import create_user, get_user, get_all_users, get_users_count
from app.database import get_db
from app.models import User as UserModel

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = get_user(db, user_id=user.user_id)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        db_user = create_user(db, user)
        return db_user
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/profile", response_model=User)
def read_profile(
    user_id: str = Query(..., description="User ID to search for"),
    db: Session = Depends(get_db)
):
    print(f"Looking for user with user_id: {user_id}")
    db_user = get_user(db, user_id=user_id)
    print(f"Found user: {db_user}")
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_user
    
@router.get("/", response_model=UserResponse)
def get_all_users_endpoint(
    skip: int = Query(0, ge=0, description="Q-ty of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="maximum of users to return"),
    db: Session = Depends(get_db)
):
    """Get all users with pagination."""
    try:
        users = get_all_users(db, skip=skip, limit=limit)
        total = get_users_count(db)
        
        return UsersListResponse(
            users=users,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        print(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



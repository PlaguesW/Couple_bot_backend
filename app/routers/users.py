from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, User
from app.crud import create_or_update_user, get_user
from app.database import get_db

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = create_or_update_user(db, user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=User)
def read_profile(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

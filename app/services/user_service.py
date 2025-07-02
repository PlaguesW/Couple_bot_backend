# from app.crud import get_user as crud_get_user
# from app.crud import create_user as crud_create_user
# from app.schemas import UserCreate, User
# from sqlalchemy.orm import Session
# from typing import Optional

# def get_or_create_user(db: Session, user_id: str) -> User:
#     db_user = crud_get_user(db, user_id=user_id)
#     if not db_user:
#         user_data = UserCreate(user_id=user_id)
#         db_user = crud_create_user(db, user_data)
#     return db_user
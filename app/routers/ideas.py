from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import IdeaCreate, Idea
from app.crud import create_idea, get_all_ideas, get_idea, delete_idea, update_idea
from app.database import get_db

router = APIRouter(prefix="/ideas", tags=["Ideas"])

@router.post("/", response_model=Idea)
def create_idea_route(idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = create_idea(db, idea)
    return db_idea

@router.get("/all", response_model=list[Idea])
def get_all_ideas_route(db: Session = Depends(get_db)):
    ideas = get_all_ideas(db)
    return ideas

@router.get("/{idea_id}", response_model=Idea)
def read_idea(idea_id: str, db: Session = Depends(get_db)):
    db_idea = get_idea(db, idea_id=idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea

@router.delete("/{idea_id}")
def delete_idea_route(idea_id: str, db: Session = Depends(get_db)):
    db_idea = get_idea(db, idea_id=idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    delete_idea(db, idea_id)
    return {"detail": "Idea deleted"}

@router.patch("/{idea_id}", response_model=Idea)
def update_idea_route(idea_id: str, updated_idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = get_idea(db, idea_id=idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    updated_idea_data = updated_idea.dict(exclude_unset=True)
    for key, value in updated_idea_data.items():
        setattr(db_idea, key, value)
    db.commit()
    db.refresh(db_idea)
    return db_idea
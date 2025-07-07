from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.idea import IdeaCreate, IdeaUpdate, IdeaResponse
from app.database import db

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("/", response_model=List[IdeaResponse])
async def get_all_ideas():
    """Get all date ideas"""
    ideas = await db.get_all_ideas()
    return [IdeaResponse(**idea) for idea in ideas]


@router.post("/", response_model=IdeaResponse)
async def create_idea(idea_data: IdeaCreate):
    """Create a new date idea"""
    idea = await db.create_idea(
        title=idea_data.title,
        description=idea_data.description,
        category=idea_data.category
    )
    return IdeaResponse(**idea)


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: int):
    """Get specific idea"""
    idea = await db.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    return IdeaResponse(**idea)


@router.patch("/{idea_id}", response_model=IdeaResponse)
async def update_idea(idea_id: int, idea_data: IdeaUpdate):
    """Update a specific idea"""
    idea = await db.update_idea(
        idea_id=idea_id,
        title=idea_data.title,
        description=idea_data.description,
        category=idea_data.category,
        is_active=idea_data.is_active
    )
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    return IdeaResponse(**idea)


@router.delete("/{idea_id}")
async def delete_idea(idea_id: int):
    """Delete an idea"""
    deleted = await db.delete_idea(idea_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    return {"message": "Idea deleted successfully"}
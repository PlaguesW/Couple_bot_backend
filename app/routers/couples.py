from fastapi import APIRouter, HTTPException, status
from app.schemas.couple import CoupleCreate, CoupleJoin, CoupleResponse
from app.database import db

router = APIRouter(prefix="/couples", tags=["couples"])


@router.post("/", response_model=CoupleResponse)
async def create_couple(couple_data: CoupleCreate):
    """Create a new couple"""
    couple = await db.create_couple(couple_data.user_id)
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in a couple"
        )
    return CoupleResponse(**couple)


@router.post("/join", response_model=CoupleResponse)
async def join_couple(join_data: CoupleJoin):
    """Join an existing couple"""
    couple = await db.join_couple(join_data.user_id, join_data.invite_code)
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite code or user already in a couple"
        )
    return CoupleResponse(**couple)


@router.get("/{couple_id}", response_model=CoupleResponse)
async def get_couple(couple_id: int):
    """Get couple information"""
    couple = await db.get_couple_by_id(couple_id)
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couple not found"
        )
    return CoupleResponse(**couple)


@router.get("/code/{invite_code}", response_model=dict)
async def generate_couple_code():
    """Generate a new couple invite code"""
    code = db.generate_invite_code()
    return {"invite_code": code}
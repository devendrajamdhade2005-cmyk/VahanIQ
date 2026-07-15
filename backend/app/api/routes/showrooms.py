"""Showroom management routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_showrooms():
    return {"message": "Get showrooms - to be implemented"}

@router.get("/{showroom_id}")
async def get_showroom(showroom_id: int):
    return {"message": f"Get showroom {showroom_id} - to be implemented"}

@router.post("/")
async def create_showroom():
    return {"message": "Create showroom - to be implemented"}

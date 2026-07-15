"""Repair case routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_repairs():
    return {"message": "Get repairs - to be implemented"}

@router.post("/")
async def create_repair():
    return {"message": "Create repair - to be implemented"}

@router.get("/{repair_id}")
async def get_repair(repair_id: int):
    return {"message": f"Get repair {repair_id} - to be implemented"}

@router.patch("/{repair_id}/status")
async def update_repair_status(repair_id: int):
    return {"message": f"Update repair {repair_id} status - to be implemented"}

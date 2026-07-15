"""Diagnosis routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_diagnoses():
    return {"message": "Get diagnoses - to be implemented"}

@router.post("/")
async def create_diagnosis():
    return {"message": "Create diagnosis - to be implemented"}

@router.get("/{diagnosis_id}")
async def get_diagnosis(diagnosis_id: int):
    return {"message": f"Get diagnosis {diagnosis_id} - to be implemented"}

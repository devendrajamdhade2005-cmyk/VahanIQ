"""Appointment management routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_appointments():
    return {"message": "Get appointments - to be implemented"}

@router.post("/")
async def create_appointment():
    return {"message": "Create appointment - to be implemented"}

@router.get("/{appointment_id}")
async def get_appointment(appointment_id: int):
    return {"message": f"Get appointment {appointment_id} - to be implemented"}

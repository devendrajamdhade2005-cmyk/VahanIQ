"""Vehicle management routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_vehicles():
    return {"message": "Get vehicles - to be implemented"}

@router.get("/{vehicle_id}")
async def get_vehicle(vehicle_id: int):
    return {"message": f"Get vehicle {vehicle_id} - to be implemented"}

@router.post("/")
async def create_vehicle():
    return {"message": "Create vehicle - to be implemented"}

@router.post("/{vehicle_id}/sensors")
async def ingest_sensor_data(vehicle_id: int):
    return {"message": f"Ingest sensor data for vehicle {vehicle_id} - to be implemented"}

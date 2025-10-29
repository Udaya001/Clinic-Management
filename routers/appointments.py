from fastapi import APIRouter, HTTPException, Depends
from models import Appointment
from schemas import AppointmentCreate, AppointmentUpdate, StandardResponse
from database import db, serialize_document, get_db
from utils import generate_unique_id

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_appointment(appointment: AppointmentCreate, db=Depends(get_db)):
    appointment_id = generate_unique_id("APT")
    new_appointment = Appointment(
        appointment_id=appointment_id,
        **appointment.dict()
    )
    
    result = await db.appointments.insert_one(new_appointment.dict(by_alias=True))
    
    created_appointment = await db.appointments.find_one({"_id": result.inserted_id})
    serialized_appointment = serialize_document(created_appointment)
    
    return StandardResponse(
        success=True,
        message="Appointment created successfully",
        data=serialized_appointment
    )

@router.get("/{appointment_id}", response_model=StandardResponse)
async def get_appointment(appointment_id: str, db=Depends(get_db)):
    appointment = await db.appointments.find_one({"appointment_id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    serialized_appointment = serialize_document(appointment)
    return StandardResponse(
        success=True,
        message="Appointment retrieved successfully",
        data=serialized_appointment
    )

@router.put("/{appointment_id}", response_model=StandardResponse)
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in appointment_update.dict().items() if v is not None}
    
    result = await db.appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    updated_appointment = await db.appointments.find_one({"appointment_id": appointment_id})
    serialized_appointment = serialize_document(updated_appointment)
    
    return StandardResponse(
        success=True,
        message="Appointment updated successfully",
        data=serialized_appointment
    )

@router.delete("/{appointment_id}", response_model=StandardResponse)
async def delete_appointment(appointment_id: str, db=Depends(get_db)):
    result = await db.appointments.delete_one({"appointment_id": appointment_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return StandardResponse(
        success=True,
        message="Appointment deleted successfully",
        data=None
    )

@router.get("/", response_model=StandardResponse)
async def get_all_appointments(db=Depends(get_db)):
    appointments = []
    async for appointment in db.appointments.find():
        appointments.append(serialize_document(appointment))
    
    return StandardResponse(
        success=True,
        message="Appointments retrieved successfully",
        data={"appointments": appointments}
    )
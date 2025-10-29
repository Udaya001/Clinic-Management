from fastapi import APIRouter, HTTPException, Depends
from models import Patient
from schemas import PatientCreate, PatientUpdate, StandardResponse
from database import db, serialize_document, get_db
from utils import generate_unique_id
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_patient(patient: PatientCreate, db=Depends(get_db)):
    patient_id = generate_unique_id("PAT")
    new_patient = Patient(
        patient_id=patient_id,
        **patient.dict()
    )
    
    result = await db.patients.insert_one(new_patient.dict(by_alias=True))
    
    created_patient = await db.patients.find_one({"_id": result.inserted_id})
    serialized_patient = serialize_document(created_patient)
    
    return StandardResponse(
        success=True,
        message="Patient created successfully",
        data=serialized_patient
    )

@router.get("/{patient_id}", response_model=StandardResponse)
async def get_patient(patient_id: str, db=Depends(get_db)):
    patient = await db.patients.find_one({"patient_id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    serialized_patient = serialize_document(patient)
    return StandardResponse(
        success=True,
        message="Patient retrieved successfully",
        data=serialized_patient
    )

@router.put("/{patient_id}", response_model=StandardResponse)
async def update_patient(patient_id: str, patient_update: PatientUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in patient_update.dict().items() if v is not None}
    
    result = await db.patients.update_one(
        {"patient_id": patient_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    updated_patient = await db.patients.find_one({"patient_id": patient_id})
    serialized_patient = serialize_document(updated_patient)
    
    return StandardResponse(
        success=True,
        message="Patient updated successfully",
        data=serialized_patient
    )

@router.delete("/{patient_id}", response_model=StandardResponse)
async def delete_patient(patient_id: str, db=Depends(get_db)):
    result = await db.patients.delete_one({"patient_id": patient_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return StandardResponse(
        success=True,
        message="Patient deleted successfully",
        data=None
    )

@router.get("/", response_model=StandardResponse)
async def get_all_patients(db=Depends(get_db)):
    patients = []
    async for patient in db.patients.find():
        patients.append(serialize_document(patient))
    
    return StandardResponse(
        success=True,
        message="Patients retrieved successfully",
        data={"patients": patients}
    )
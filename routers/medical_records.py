from fastapi import APIRouter, HTTPException, Depends
from models import MedicalRecord
from schemas import MedicalRecordCreate, MedicalRecordUpdate, StandardResponse
from database import db, serialize_document, get_db
from utils import generate_unique_id

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_medical_record(record: MedicalRecordCreate, db=Depends(get_db)):
    record_id = generate_unique_id("REC")
    new_record = MedicalRecord(
        record_id=record_id,
        **record.dict()
    )
    
    result = await db.medical_records.insert_one(new_record.dict(by_alias=True))
    
    created_record = await db.medical_records.find_one({"_id": result.inserted_id})
    serialized_record = serialize_document(created_record)
    
    return StandardResponse(
        success=True,
        message="Medical record created successfully",
        data=serialized_record
    )

@router.get("/{record_id}", response_model=StandardResponse)
async def get_medical_record(record_id: str, db=Depends(get_db)):
    record = await db.medical_records.find_one({"record_id": record_id})
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    serialized_record = serialize_document(record)
    return StandardResponse(
        success=True,
        message="Medical record retrieved successfully",
        data=serialized_record
    )

@router.put("/{record_id}", response_model=StandardResponse)
async def update_medical_record(record_id: str, record_update: MedicalRecordUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in record_update.dict().items() if v is not None}
    
    result = await db.medical_records.update_one(
        {"record_id": record_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    updated_record = await db.medical_records.find_one({"record_id": record_id})
    serialized_record = serialize_document(updated_record)
    
    return StandardResponse(
        success=True,
        message="Medical record updated successfully",
        data=serialized_record
    )

@router.delete("/{record_id}", response_model=StandardResponse)
async def delete_medical_record(record_id: str, db=Depends(get_db)):
    result = await db.medical_records.delete_one({"record_id": record_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    return StandardResponse(
        success=True,
        message="Medical record deleted successfully",
        data=None
    )

@router.get("/", response_model=StandardResponse)
async def get_all_medical_records(db=Depends(get_db)):
    records = []
    async for record in db.medical_records.find():
        records.append(serialize_document(record))
    
    return StandardResponse(
        success=True,
        message="Medical records retrieved successfully",
        data={"records": records}
    )
from fastapi import APIRouter, HTTPException, Depends
from models import Staff
from schemas import StaffCreate, StaffUpdate, StandardResponse
from database import db, serialize_document, get_db
from utils import generate_unique_id

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_staff(staff: StaffCreate, db=Depends(get_db)):
    staff_id = generate_unique_id("STF")
    new_staff = Staff(
        staff_id=staff_id,
        **staff.dict()
    )
    
    result = await db.staff.insert_one(new_staff.dict(by_alias=True))
    
    created_staff = await db.staff.find_one({"_id": result.inserted_id})
    serialized_staff = serialize_document(created_staff)
    
    return StandardResponse(
        success=True,
        message="Staff member created successfully",
        data=serialized_staff
    )

@router.get("/{staff_id}", response_model=StandardResponse)
async def get_staff(staff_id: str, db=Depends(get_db)):
    staff = await db.staff.find_one({"staff_id": staff_id})
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    serialized_staff = serialize_document(staff)
    return StandardResponse(
        success=True,
        message="Staff member retrieved successfully",
        data=serialized_staff
    )

@router.put("/{staff_id}", response_model=StandardResponse)
async def update_staff(staff_id: str, staff_update: StaffUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in staff_update.dict().items() if v is not None}
    
    result = await db.staff.update_one(
        {"staff_id": staff_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    updated_staff = await db.staff.find_one({"staff_id": staff_id})
    serialized_staff = serialize_document(updated_staff)
    
    return StandardResponse(
        success=True,
        message="Staff member updated successfully",
        data=serialized_staff
    )

@router.delete("/{staff_id}", response_model=StandardResponse)
async def delete_staff(staff_id: str, db=Depends(get_db)):
    result = await db.staff.delete_one({"staff_id": staff_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return StandardResponse(
        success=True,
        message="Staff member deleted successfully",
        data=None
    )

@router.get("/", response_model=StandardResponse)
async def get_all_staff(db=Depends(get_db)):
    staff = []
    async for s in db.staff.find():
        staff.append(serialize_document(s))
    
    return StandardResponse(
        success=True,
        message="Staff members retrieved successfully",
        data={"staff": staff}
    )
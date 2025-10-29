from fastapi import APIRouter, HTTPException, Depends
from models import Billing
from schemas import BillingCreate, BillingUpdate, StandardResponse
from database import db, serialize_document, get_db
from utils import generate_unique_id

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_billing(billing: BillingCreate, db=Depends(get_db)):
    bill_id = generate_unique_id("BILL")
    new_billing = Billing(
        bill_id=bill_id,
        **billing.dict()
    )
    
    result = await db.billing.insert_one(new_billing.dict(by_alias=True))
    
    created_billing = await db.billing.find_one({"_id": result.inserted_id})
    serialized_billing = serialize_document(created_billing)
    
    return StandardResponse(
        success=True,
        message="Billing record created successfully",
        data=serialized_billing
    )

@router.get("/{bill_id}", response_model=StandardResponse)
async def get_billing(bill_id: str, db=Depends(get_db)):
    billing = await db.billing.find_one({"bill_id": bill_id})
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    serialized_billing = serialize_document(billing)
    return StandardResponse(
        success=True,
        message="Billing record retrieved successfully",
        data=serialized_billing
    )

@router.put("/{bill_id}", response_model=StandardResponse)
async def update_billing(bill_id: str, billing_update: BillingUpdate, db=Depends(get_db)):
    update_data = {k: v for k, v in billing_update.dict().items() if v is not None}
    
    result = await db.billing.update_one(
        {"bill_id": bill_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    updated_billing = await db.billing.find_one({"bill_id": bill_id})
    serialized_billing = serialize_document(updated_billing)
    
    return StandardResponse(
        success=True,
        message="Billing record updated successfully",
        data=serialized_billing
    )

@router.delete("/{bill_id}", response_model=StandardResponse)
async def delete_billing(bill_id: str, db=Depends(get_db)):
    result = await db.billing.delete_one({"bill_id": bill_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    return StandardResponse(
        success=True,
        message="Billing record deleted successfully",
        data=None
    )

@router.get("/", response_model=StandardResponse)
async def get_all_billing(db=Depends(get_db)):
    billing = []
    async for bill in db.billing.find():
        billing.append(serialize_document(bill))
    
    return StandardResponse(
        success=True,
        message="Billing records retrieved successfully",
        data={"billing": billing}
    )
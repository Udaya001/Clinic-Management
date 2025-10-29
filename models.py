from typing import Optional, Any
from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer, field_validator
from pydantic_core import core_schema


# Custom ObjectId type for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                )
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


# Base model
class MongoBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True


# Models
class User(MongoBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_name: str
    email: str
    password: str
    role: str = "admin"

    @field_serializer('id')
    def serialize_id(self, value: PyObjectId, _info):
        return str(value)


class Patient(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    patient_id: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    contact_number: str
    email: str
    address: str
    emergency_contact: str

    @field_serializer('id')
    def serialize_id(self, value: Optional[PyObjectId], _info):
        return str(value) if value else None


class Staff(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    staff_id: Optional[str] = None
    first_name: str
    last_name: str
    role: str
    specialization: Optional[str] = None
    contact_number: str
    email: str
    hire_date: str

    @field_serializer('id')
    def serialize_id(self, value: Optional[PyObjectId], _info):
        return str(value) if value else None


class Appointment(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    appointment_id: Optional[str] = None
    patient_id: str
    doctor_id: str
    appointment_date: str
    status: str = "Scheduled"  # Scheduled, Completed, Cancelled, No-Show
    reason_for_visit: str
    notes: Optional[str] = None

    @field_serializer('id')
    def serialize_id(self, value: Optional[PyObjectId], _info):
        return str(value) if value else None


class MedicalRecord(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    record_id: Optional[str] = None
    patient_id: str
    doctor_id: str
    visit_date: str
    diagnosis: str
    treatment: str
    lab_results: Optional[str] = None
    follow_up_required: bool = False

    @field_serializer('id')
    def serialize_id(self, value: Optional[PyObjectId], _info):
        return str(value) if value else None


class Billing(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    bill_id: Optional[str] = None
    patient_id: str
    appointment_id: str
    total_amount: float
    paid_amount: float
    payment_method: str  # Cash, Card, Online
    payment_status: str = "Pending"  # Pending, Paid, Partial, Cancelled
    billing_date: str

    @field_serializer('id')
    def serialize_id(self, value: Optional[PyObjectId], _info):
        return str(value) if value else None
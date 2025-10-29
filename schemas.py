from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class RegisterRequest(BaseModel):
    user_name: str
    email: str
    phone: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Patient Schemas
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    contact_number: str
    email: str
    address: str
    emergency_contact: str

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

# Staff Schemas
class StaffCreate(BaseModel):
    first_name: str
    last_name: str
    role: str
    specialization: Optional[str] = None
    contact_number: str
    email: str
    hire_date: str

class StaffUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    hire_date: Optional[str] = None

# Appointment Schemas
class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_date: str
    reason_for_visit: str
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    appointment_date: Optional[str] = None
    status: Optional[str] = None  # Scheduled, Completed, Cancelled, No-Show
    reason_for_visit: Optional[str] = None
    notes: Optional[str] = None

# Medical Record Schemas
class MedicalRecordCreate(BaseModel):
    patient_id: str
    doctor_id: str
    visit_date: str
    diagnosis: str
    treatment: str
    lab_results: Optional[str] = None
    follow_up_required: bool = False

class MedicalRecordUpdate(BaseModel):
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    visit_date: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    lab_results: Optional[str] = None
    follow_up_required: Optional[bool] = None

# Billing Schemas
class BillingCreate(BaseModel):
    patient_id: str
    appointment_id: str
    total_amount: float
    paid_amount: float
    payment_method: str  # Cash, Card, Online
    billing_date: str

class BillingUpdate(BaseModel):
    patient_id: Optional[str] = None
    appointment_id: Optional[str] = None
    total_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    payment_method: Optional[str] = None  # Cash, Card, Online
    payment_status: Optional[str] = None  # Pending, Paid, Partial, Cancelled
    billing_date: Optional[str] = None
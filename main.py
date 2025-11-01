from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, patients, staff, appointments, medical_records, billing, dashboard
from database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Clinic Management System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(medical_records.router, prefix="/api/medical-records", tags=["Medical Records"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])

@app.get("/")
def read_root():
    return {"message": "Clinic Management System API"}
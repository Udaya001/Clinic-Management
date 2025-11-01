from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from database import get_db
from auth import get_current_user
from schemas import StandardResponse

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def get_dashboard_data(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Get comprehensive dashboard data"""
    
    try:
        # Get today's date
        today = datetime.now().date()
        start_of_today = datetime.combine(today, datetime.min.time())
        end_of_today = datetime.combine(today, datetime.max.time())
        
        # Calculate dates for comparison
        yesterday = today - timedelta(days=1)
        start_of_yesterday = datetime.combine(yesterday, datetime.min.time())
        end_of_yesterday = datetime.combine(yesterday, datetime.max.time())
        
        last_month = today.replace(day=1) - timedelta(days=1)
        start_of_last_month = datetime.combine(last_month.replace(day=1), datetime.min.time())
        end_of_last_month = datetime.combine(last_month.replace(day=last_month.day), datetime.max.time())
        
        # Total Patients
        total_patients = await db.patients.count_documents({})
        
        # Patients from last month (for comparison)
        patients_last_month = await db.patients.count_documents({
            "created_at": {"$gte": start_of_last_month, "$lte": end_of_last_month}
        })
        
        # Appointments Today
        appointments_today = await db.appointments.count_documents({
            "appointment_date": {"$gte": start_of_today.isoformat(), "$lte": end_of_today.isoformat()}
        })
        
        # Appointments Yesterday (for comparison)
        appointments_yesterday = await db.appointments.count_documents({
            "appointment_date": {"$gte": start_of_yesterday.isoformat(), "$lte": end_of_yesterday.isoformat()}
        })
        
        # Staff Members
        staff_members = await db.staff.count_documents({})
        
        # Staff this month (for comparison)
        staff_this_month = await db.staff.count_documents({
            "hire_date": {"$gte": start_of_today.isoformat()}
        })
        
        # Total Revenue
        # Sum all paid amounts from billing records
        total_revenue_cursor = db.billing.aggregate([
            {"$match": {"payment_status": "Paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$paid_amount"}}}
        ])
        total_revenue_result = await total_revenue_cursor.to_list(length=1)
        total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0.0
        
        # Revenue from last month (for comparison)
        revenue_last_month_cursor = db.billing.aggregate([
            {"$match": {
                "payment_status": "Paid",
                "billing_date": {"$gte": start_of_last_month.isoformat(), "$lte": end_of_last_month.isoformat()}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$paid_amount"}}}
        ])
        revenue_last_month_result = await revenue_last_month_cursor.to_list(length=1)
        revenue_last_month = revenue_last_month_result[0]["total"] if revenue_last_month_result else 0.0
        
        # Today's Appointments (with patient and doctor names)
        today_appointments_cursor = db.appointments.find({
            "appointment_date": {"$gte": start_of_today.isoformat(), "$lte": end_of_today.isoformat()}
        }).sort("appointment_date", 1).limit(4)
        
        today_appointments = []
        async for appointment in today_appointments_cursor:
            # Get patient name
            patient = await db.patients.find_one({"patient_id": appointment["patient_id"]})
            patient_name = f"{patient['first_name']} {patient['last_name']}" if patient else "Unknown Patient"
            
            # Get doctor name
            doctor = await db.staff.find_one({"staff_id": appointment["doctor_id"]})
            doctor_name = f"Dr. {doctor['first_name']} {doctor['last_name']}" if doctor else "Unknown Doctor"
            
            today_appointments.append({
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "time": appointment["appointment_date"].split('T')[1][:5] + " " + ("AM" if int(appointment["appointment_date"].split('T')[1][:2]) < 12 else "PM"),
                "status": appointment["status"]
            })
        
        # Appointment Status Counts
        confirmed_count = await db.appointments.count_documents({
            "appointment_date": {"$gte": start_of_today.isoformat(), "$lte": end_of_today.isoformat()},
            "status": "Confirmed"
        })
        
        pending_count = await db.appointments.count_documents({
            "appointment_date": {"$gte": start_of_today.isoformat(), "$lte": end_of_today.isoformat()},
            "status": "Scheduled"
        })
        
        cancelled_count = await db.appointments.count_documents({
            "appointment_date": {"$gte": start_of_today.isoformat(), "$lte": end_of_today.isoformat()},
            "status": "Cancelled"
        })
        
        # Recent Patients (last 3 by visit date)
        recent_patients_cursor = db.patients.find({}).sort("created_at", -1).limit(3)
        recent_patients = []
        async for patient in recent_patients_cursor:
            # Get last visit date (from medical records)
            last_visit_record = await db.medical_records.find_one(
                {"patient_id": patient["patient_id"]}, 
                sort=[("visit_date", -1)]
            )
            last_visit = last_visit_record["visit_date"] if last_visit_record else "No visits yet"
            
            recent_patients.append({
                "name": f"{patient['first_name']} {patient['last_name']}",
                "phone": patient["contact_number"],
                "last_visit": last_visit.split('T')[0] if last_visit != "No visits yet" else "No visits yet"
            })
        
        # Calculate percentage changes
        patient_change = ((total_patients - patients_last_month) / patients_last_month * 100) if patients_last_month > 0 else 0
        appointment_change = ((appointments_today - appointments_yesterday) / appointments_yesterday * 100) if appointments_yesterday > 0 else 0
        staff_change = staff_this_month
        revenue_change = ((total_revenue - revenue_last_month) / revenue_last_month * 100) if revenue_last_month > 0 else 0
        
        dashboard_data = {
            "stats": {
                "total_patients": total_patients,
                "patients_change": f"+{int(patient_change)}% from last month" if patient_change > 0 else f"{int(patient_change)}% from last month",
                "appointments_today": appointments_today,
                "appointments_change": f"+{appointments_today - appointments_yesterday} than yesterday" if appointments_today > appointments_yesterday else f"{appointments_today - appointments_yesterday} than yesterday",
                "staff_members": staff_members,
                "staff_change": f"+{staff_change} this month",
                "total_revenue": f"${total_revenue:,.2f}",
                "revenue_change": f"+{int(revenue_change)}% from last month" if revenue_change > 0 else f"{int(revenue_change)}% from last month"
            },
            "today_appointments": today_appointments,
            "appointment_stats": {
                "confirmed": confirmed_count,
                "pending": pending_count,
                "cancelled": cancelled_count
            },
            "recent_patients": recent_patients,
            "quick_actions": [
                {"label": "Add New Patient", "icon": "+", "route": "/patients/new"},
                {"label": "Schedule Appointment", "icon": "+", "route": "/appointments/new"},
                {"label": "Add Staff Member", "icon": "+", "route": "/staff/new"},
                {"label": "Create Medical Record", "icon": "+", "route": "/medical-records/new"},
                {"label": "View Billing & Invoices", "icon": "$", "route": "/billing"}
            ]
        }
        
        return StandardResponse(
            success=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")
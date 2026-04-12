from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database.db import reports_collection, users_collection
from backend.auth import decode_token
from backend.models import ReportStatusUpdate
from bson import ObjectId

router = APIRouter(prefix="/admin", tags=["Admin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_admin(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = users_collection.find_one({"username": payload.get("sub")})
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user


@router.put("/report/{report_id}/status")
def update_status(report_id: str, data: ReportStatusUpdate, admin=Depends(get_admin)):
    valid = ["Pending", "In Progress", "Resolved"]
    if data.status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    result = reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"status": data.status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Status updated"}


@router.get("/stats")
def admin_stats(admin=Depends(get_admin)):
    total = reports_collection.count_documents({})
    pending = reports_collection.count_documents({"status": "Pending"})
    in_progress = reports_collection.count_documents({"status": "In Progress"})
    resolved = reports_collection.count_documents({"status": "Resolved"})
    high_risk = reports_collection.count_documents({"priority": "High"})
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_risk": high_risk,
    }
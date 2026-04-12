from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database.db import reports_collection
from backend.auth import decode_token
from database.db import users_collection
from backend.models import ReportCreate
from backend.ai_engine import analyze_report
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = users_collection.find_one({"username": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.post("/submit")
def submit_report(data: ReportCreate, current_user=Depends(get_current_user)):
    ai_result = analyze_report(data.description)
    report = {
        "user_id": str(current_user["_id"]),
        "username": current_user["username"],
        "description": data.description,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "location_label": data.location_label,
        "image_base64": data.image_base64,
        "category": ai_result["category"],
        "risk_score": ai_result["risk_score"],
        "priority": ai_result["priority"],
        "status": "Pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    result = reports_collection.insert_one(report)
    report["_id"] = str(result.inserted_id)
    return {"message": "Report submitted", "report": report}


@router.get("/my")
def my_reports(current_user=Depends(get_current_user)):
    docs = list(reports_collection.find({"user_id": str(current_user["_id"])}))
    return [serialize(d) for d in docs]


@router.get("/all")
def all_reports(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    docs = list(reports_collection.find({}))
    return [serialize(d) for d in docs]


@router.get("/analytics")
def analytics(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    pipeline = [
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "avg_risk": {"$avg": "$risk_score"}
        }}
    ]
    category_stats = list(reports_collection.aggregate(pipeline))
    priority_pipeline = [
        {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
    ]
    priority_stats = list(reports_collection.aggregate(priority_pipeline))
    all_docs = list(reports_collection.find({}, {"latitude": 1, "longitude": 1, "risk_score": 1, "priority": 1}))
    return {
        "category_stats": category_stats,
        "priority_stats": priority_stats,
        "map_data": [serialize(d) for d in all_docs],
    }
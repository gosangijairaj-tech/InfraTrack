import logging
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from bson import ObjectId
from bson.errors import InvalidId
from database.db import reports_collection, categories_collection, settings_collection
from backend.dependencies import get_current_user
from backend.models import ReportCreate
from backend.ai_engine import analyze_report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])
_subscribers: list[asyncio.Queue] = []

def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def _broadcast(report: dict) -> None:
    import json
    payload = json.dumps(report, default=str)
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        _subscribers.remove(q)

@router.post("/submit", status_code=201)
def submit_report(data: ReportCreate, current_user: dict = Depends(get_current_user)):
    try:
        ai_result = analyze_report(data.description)
    except Exception as e:
        logger.error(f"AI engine crashed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")

    report = {
        "user_id":           str(current_user["_id"]),
        "username":          current_user["username"],
        "description":       data.description,
        "latitude":          data.latitude,
        "longitude":         data.longitude,
        "location_label":    data.location_label,
        "location_source":   data.location_source,
        "location_accuracy": data.location_accuracy,
        "image_base64":      data.image_base64,
        "category":          ai_result["category"],
        "risk_score":        ai_result["risk_score"],
        "priority":          ai_result["priority"],
        "reasoning":         ai_result.get("reasoning", ""),
        "affected_population": ai_result.get("affected_population", ""),
        "recommended_action":  ai_result.get("recommended_action", ""),
        "ai_powered":        ai_result.get("ai_powered", False),
        "status":            "Pending",
        "created_at":        datetime.utcnow().isoformat(),
    }

    result  = reports_collection.insert_one(report)
    report["_id"] = str(result.inserted_id)
    logger.info(f"Report submitted by {current_user['username']} — score={ai_result['risk_score']}")

    # FIX #9 — broadcast to all SSE listeners
    _broadcast(report)

    return {"success": True, "message": "Report submitted successfully.", "report": report}

@router.get("/my")
def my_reports(current_user: dict = Depends(get_current_user)):
    docs = list(reports_collection.find({"user_id": str(current_user["_id"])}).sort("created_at", -1))
    return {"success": True, "reports": [_serialize(d) for d in docs]}

@router.get("/all")
def all_reports(
    category: str = None,
    priority: str = None,
    status:   str = None,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")

    query = {}
    if category: query["category"] = category
    if priority: query["priority"] = priority
    if status:   query["status"]   = status

    docs = list(reports_collection.find(query).sort("created_at", -1))
    return {"success": True, "reports": [_serialize(d) for d in docs]}

@router.get("/analytics")
def analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "authority"]:
        raise HTTPException(status_code=403, detail="Admin access required.")

    cat_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1},
                    "avg_risk": {"$avg": "$risk_score"}}}
    ]
    prio_pipeline = [{"$group": {"_id": "$priority", "count": {"$sum": 1}}}]
    status_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]

    map_docs = list(reports_collection.find(
        {},
        {"latitude": 1, "longitude": 1, "risk_score": 1,
         "priority": 1, "category": 1, "status": 1}
    ))

    return {
        "success":        True,
        "category_stats": list(reports_collection.aggregate(cat_pipeline)),
        "priority_stats": list(reports_collection.aggregate(prio_pipeline)),
        "status_stats":   list(reports_collection.aggregate(status_pipeline)),
        "map_data":       [_serialize(d) for d in map_docs],
    }
@router.get("/categories")
def get_categories():
    cats = list(categories_collection.find({"active": True}, {"_id": 0}))
    return {"success": True, "categories": cats}

@router.get("/stream")
async def stream_reports(current_user: dict = Depends(get_current_user)):
    """
    Server-Sent Events endpoint. Connect once; receive new reports as JSON
    events in real time without polling or page refresh.
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=50)
    _subscribers.append(queue)
    logger.info(f"SSE client connected: {current_user['username']} (total={len(_subscribers)})")

    async def event_generator() -> AsyncGenerator[str, None]:
        yield "event: connected\ndata: {\"status\": \"listening\"}\n\n"
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=25)
                    yield f"event: new_report\ndata: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield "event: heartbeat\ndata: {}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in _subscribers:
                _subscribers.remove(queue)
            logger.info(f"SSE client disconnected: {current_user['username']}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
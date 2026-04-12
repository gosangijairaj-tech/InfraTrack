import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT  = 30


def _call(method: str, path: str, token: str = None, **kwargs) -> tuple[bool, dict]:
    url     = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.request(method, url, headers=headers, timeout=TIMEOUT, **kwargs)
        data = resp.json()
        if resp.status_code >= 400:
            logger.warning(f"API {method} {path} → {resp.status_code}: {data}")
            return False, data
        return True, data
    except requests.ConnectionError:
        msg = "Cannot reach backend. Is the FastAPI server running?"
        logger.error(msg)
        return False, {"error": msg}
    except requests.Timeout:
        msg = "Request timed out. Backend may be overloaded."
        logger.error(msg)
        return False, {"error": msg}
    except Exception as e:
        logger.exception(f"Unexpected error calling {path}: {e}")
        return False, {"error": str(e)}


def register_user(username: str, email: str, password: str):
    return _call("POST", "/auth/register",
                 json={"username": username, "email": email, "password": password})


def login_user(username: str, password: str):
    return _call("POST", "/auth/login",
                 json={"username": username, "password": password})


def submit_report(token: str, description: str, lat: float, lon: float,
                  location_label: str, image_b64: str,
                  location_source: str = "manual", location_accuracy: float = None):
    return _call("POST", "/reports/submit", token=token, json={
        "description":       description,
        "latitude":          lat,
        "longitude":         lon,
        "location_label":    location_label,
        "image_base64":      image_b64,
        "location_source":   location_source,
        "location_accuracy": location_accuracy,
    })


def get_my_reports(token: str):
    return _call("GET", "/reports/my", token=token)


def get_all_reports(token: str, category=None, priority=None, status=None):
    params = {}
    if category: params["category"] = category
    if priority: params["priority"] = priority
    if status:   params["status"]   = status
    return _call("GET", "/reports/all", token=token, params=params)


def update_report_status(token: str, report_id: str, status: str):
    return _call("PUT", f"/admin/report/{report_id}/status", token=token,
                 json={"status": status})


def get_analytics(token: str):
    return _call("GET", "/reports/analytics", token=token)


def get_admin_stats(token: str):
    return _call("GET", "/admin/stats", token=token)


def get_categories():
    return _call("GET", "/reports/categories")


def get_admin_config(token: str):
    return _call("GET", "/admin/config", token=token)


def update_thresholds(token: str, low_max: int, medium_max: int):
    return _call("PUT", "/admin/config/thresholds", token=token,
                 params={"low_max": low_max, "medium_max": medium_max})


def update_category_config(token: str, category_name: str, base_score: int, active: bool):
    return _call("PUT", f"/admin/config/category/{category_name}", token=token,
                 params={"base_score": base_score, "active": active})


def health_check():
    return _call("GET", "/health")

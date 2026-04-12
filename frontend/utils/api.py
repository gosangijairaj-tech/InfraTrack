import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def register_user(username: str, email: str, password: str):
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username, "email": email, "password": password
    })
    return r.status_code, r.json()


def login_user(username: str, password: str):
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username, "password": password
    })
    return r.status_code, r.json()


def submit_report(token: str, description: str, lat: float, lon: float,
                  location_label: str, image_b64: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/reports/submit", json={
        "description": description,
        "latitude": lat,
        "longitude": lon,
        "location_label": location_label,
        "image_base64": image_b64,
    }, headers=headers)
    return r.status_code, r.json()


def get_my_reports(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/reports/my", headers=headers)
    return r.status_code, r.json()


def get_all_reports(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/reports/all", headers=headers)
    return r.status_code, r.json()


def update_report_status(token: str, report_id: str, status: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(f"{BASE_URL}/admin/report/{report_id}/status",
                     json={"status": status}, headers=headers)
    return r.status_code, r.json()


def get_analytics(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/reports/analytics", headers=headers)
    return r.status_code, r.json()


def get_admin_stats(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    return r.status_code, r.json()
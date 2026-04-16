from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class ReportCreate(BaseModel):
    description: str
    latitude: float
    longitude: float
    location_label: Optional[str] = ""
    image_base64: Optional[str] = ""
    location_source: Optional[str] = "manual"
    location_accuracy: Optional[float] = None


class ReportStatusUpdate(BaseModel):
    status: str  # "pending" | "in_progress" | "resolved"
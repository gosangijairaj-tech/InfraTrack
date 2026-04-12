import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database.db import users_collection
from backend.auth import decode_token

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please log in again.")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token payload missing subject.")
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="Account not found.")
    return user


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return current_user

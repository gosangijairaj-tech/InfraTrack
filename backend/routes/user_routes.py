from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database.db import users_collection
from backend.auth import hash_password, verify_password, create_access_token, decode_token
from backend.models import UserRegister, UserLogin
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = users_collection.find_one({"username": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register")
def register(data: UserRegister):
    if users_collection.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "username": data.username,
        "email": data.email,
        "password": hash_password(data.password),
        "role": "user",
    }
    result = users_collection.insert_one(user_doc)
    return {"message": "Registration successful", "user_id": str(result.inserted_id)}


@router.post("/login")
def login(data: UserLogin):
    user = users_collection.find_one({"username": data.username})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "role": user["role"],
    }


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"],
    }
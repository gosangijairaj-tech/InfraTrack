import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "infratrack")

if not MONGO_URI:
    raise EnvironmentError("MONGO_URI is not set in .env")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    logger.info("MongoDB Atlas connected successfully.")
except ConnectionFailure as e:
    logger.critical(f"MongoDB connection failed: {e}")
    raise

db = client[DB_NAME]

users_collection      = db["users"]
reports_collection    = db["reports"]
categories_collection = db["categories"]   # FIX #8 — config stored in DB
settings_collection   = db["settings"]     # FIX #8 — thresholds stored in DB

# ── Indexes ──────────────────────────────────────────────────────────────────
try:
    users_collection.create_index("username",  unique=True)
    users_collection.create_index("email",     unique=True)
    reports_collection.create_index([("user_id",    ASCENDING)])
    reports_collection.create_index([("risk_score", DESCENDING)])
    reports_collection.create_index([("category",   ASCENDING)])
    reports_collection.create_index([("status",     ASCENDING)])
    reports_collection.create_index([("created_at", DESCENDING)])
    logger.info("Indexes ensured.")
except OperationFailure as e:
    logger.warning(f"Index creation warning: {e}")


def seed_config():
    """
    FIX #8 — Seed categories and scoring thresholds into MongoDB so they
    can be edited without touching code.
    """
    if categories_collection.count_documents({}) == 0:
        categories_collection.insert_many([
            {"name": "Road Damage",          "base_score": 40, "icon": "🛣️",  "active": True},
            {"name": "Waste Management",     "base_score": 25, "icon": "🗑️",  "active": True},
            {"name": "Electrical Issues",    "base_score": 55, "icon": "⚡",   "active": True},
            {"name": "Water Leakage",        "base_score": 45, "icon": "💧",   "active": True},
            {"name": "Illegal Construction", "base_score": 35, "icon": "🏗️",  "active": True},
        ])
        logger.info("Category config seeded.")

    if settings_collection.count_documents({"key": "priority_thresholds"}) == 0:
        settings_collection.insert_one({
            "key":        "priority_thresholds",
            "low_max":    30,
            "medium_max": 70,
        })
        logger.info("Priority threshold config seeded.")


seed_config()
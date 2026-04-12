import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(dotenv_path="/workspaces/InfraTrack/.env")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "infratrack")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
reports_collection = db["reports"]

# Create indexes
users_collection.create_index("username", unique=True)
users_collection.create_index("email", unique=True)
reports_collection.create_index("user_id")
reports_collection.create_index("risk_score")
reports_collection.create_index("category")

# import os
# from pymongo import MongoClient
# from dotenv import load_dotenv

# load_dotenv(dotenv_path="/workspaces/InfraTrack/.env")
# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME", "infratrack")

# # 🔴 Safety check
# if not MONGO_URI:
#     raise ValueError("❌ MONGO_URI is not set. Check your .env file")

# # ✅ Create client safely
# client = MongoClient(
#     MONGO_URI,
#     serverSelectionTimeoutMS=5000  # fail fast
# )

# db = client[DB_NAME]

# users_collection = db["users"]
# reports_collection = db["reports"]

# # ✅ Safe index creation (won't crash app)
# def create_indexes():
#     try:
#         users_collection.create_index("username", unique=True)
#         users_collection.create_index("email", unique=True)
#         reports_collection.create_index("user_id")
#         reports_collection.create_index("risk_score")
#         reports_collection.create_index("category")
#         print("✅ Indexes created")
#     except Exception as e:
#         print("⚠️ Index creation skipped:", e)

# # 🔥 Call safely
# create_indexes()
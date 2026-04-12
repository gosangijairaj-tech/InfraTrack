import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

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
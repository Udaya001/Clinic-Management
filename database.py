from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()



MONGODB_URL = "mongodb://localhost:27017/clinic_db"
client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await client.server_info()  # verify connection

        database = client.get_default_database()
        db = database if database is not None else client["clinic_db"]

        # Create "users" collection only if it does not exist
        existing_collections = await db.list_collection_names()
        if "users" not in existing_collections:
            await db.create_collection("users")

        print(f"Connected to MongoDB. Using database: {db.name}")

    except ServerSelectionTimeoutError:
        raise ConnectionError("Unable to connect to MongoDB at provided URL.")


async def close_mongo_connection():
    global client
    if client:
        client.close()

# Helpers
def object_id_to_str(id: ObjectId) -> str:
    return str(id)

def str_to_object_id(id: str) -> ObjectId:
    return ObjectId(id)

def serialize_document(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# database.py
async def get_db():
    global db
    if db is None:
        await connect_to_mongo()
    return db


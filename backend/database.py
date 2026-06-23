from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import os

# MongoDB client
client = None
db = None

async def connect_db():
    """Connect to MongoDB"""
    global client, db
    mongo_url = os.environ.get("MONGO_URL", settings.MONGO_URL)
    db_name = os.environ.get("DB_NAME", settings.DB_NAME)
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.login_attempts.create_index("identifier")
    await db.families.create_index("join_code", unique=True)
    
    print(f"✅ Connected to MongoDB: {db_name}")

async def disconnect_db():
    """Disconnect from MongoDB"""
    global client
    if client:
        client.close()
        print("✅ Disconnected from MongoDB")

def get_db():
    """Get database instance"""
    return db

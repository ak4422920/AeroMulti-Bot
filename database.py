import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB using the URI from your environment variables
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client['AeroMulti_DB']

# Collections (folders) for our data
users_col = db['users']
groups_col = db['groups']
shared_files = db['shared_files']

async def init_db():
    try:
        await client.admin.command('ping')
        print("✅ MongoDB Connected Successfully!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")


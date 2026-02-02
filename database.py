import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB using the URI from your environment variables
# Make sure MONGO_URI is added in your Koyeb settings!
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client['AeroMulti_DB']

# --- Collections (Think of these as tables/folders) ---
users_col = db['users']           # For Karma and AFK
groups_col = db['groups']         # For Admin and Night Mode
files_col = db['shared_files']    # For the File Sharing System (Fixes your error!)

async def init_db():
    try:
        # Check if the connection is alive
        await client.admin.command('ping')
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")

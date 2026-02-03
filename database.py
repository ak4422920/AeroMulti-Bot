import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client['AeroMulti_V2']

# Collections
users_col = db['users']
post_col = db['posted_movies'] # Track autoposts

async def test_db_connection():
    try:
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return False

async def is_movie_posted(movie_id):
    """Check if a movie has already been sent to the channel"""
    found = await post_col.find_one({"movie_id": movie_id})
    return bool(found)

async def save_posted_movie(movie_id):
    """Save movie ID to avoid duplicates"""
    await post_col.insert_one({"movie_id": movie_id})

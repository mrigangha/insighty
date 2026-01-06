from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://madhumitagupta77_db_user:vJJdIlg5vCFzfUJG@users.codwn5q.mongodb.net/?appName=users"

client = MongoClient(uri, server_api=ServerApi("1"))
client.admin.command("ping")

print("✅ MongoDB connected successfully")

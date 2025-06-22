import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
uri = os.getenv("API_KEY")
# uri = "mongodb+srv://<db_username>:<db_password>@judgejam.5bpp3ii.mongodb.net/?retryWrites=true&w=majority&appName=JudgeJam"
print(uri)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

group_db = client["groups"]
tutorial = group_db.tutorial
print(tutorial)


# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

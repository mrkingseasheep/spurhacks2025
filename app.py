import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
uri = os.getenv("API_KEY")
# uri = "mongodb+srv://<db_username>:<db_password>@judgejam.5bpp3ii.mongodb.net/?retryWrites=true&w=majority&appName=JudgeJam"
print(uri)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# --------- #

park_db = client["ontario_parks"]
campsites = park_db["campsites"]


@app.route("/api/items")
def get_items():
    camps = list(campsites.find({}, {"_id: 0"}))
    return jsonify(camps)


if __name__ == "__main__":
    app.run(debug=True)

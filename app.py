import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# THIS IS A BUFFER COMMIT


load_dotenv()
uri = os.getenv("API_KEY")
# uri = "mongodb+srv://<db_username>:<db_password>@judgejam.5bpp3ii.mongodb.net/?retryWrites=true&w=majority&appName=JudgeJam"
print(uri)

app = Flask(__name__)
CORS(app)

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
cursor = campsites.find()


@app.route("/api/items")
def get_items():
    print("getting itmes")
    next_camp = next(cursor, None)
    if not next_camp:
        return jsonify({"message": "No more items"})

    # Convert _id to string
    if "_id" in next_camp:
        next_camp["_id"] = str(next_camp["_id"])
        print(next_camp["_id"])

    return jsonify(next_camp)


results_db = client["results"]
likes = results_db["likes"]
hates = results_db["hates"]


@app.route("/submit", methods=["POST"])
def submit():
    data = request.json  # Expecting JSON data from client
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if data["likes"]:
        result = likes.insert_one(data)
    else:
        result = hates.insert_one(data)

    return jsonify({"message": "Data inserted", "id": str(result.inserted_id)})


@app.route("/api/top-campsites")
def top_campsites():
    from Backend.SwipeStats import (
        get_top_campsites,
    )  # You may need to adjust the import path

    top_2 = get_top_campsites(2)
    return jsonify(top_2)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

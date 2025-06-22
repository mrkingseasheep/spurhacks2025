import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

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
# cursor = campsites.find({}, {"_id": 0})
cursor = campsites.find()


@app.route("/api/items")
def get_items():
    # camps = list(campsites.find({}, {"_id: 0"}))
    # return jsonify(camps)
    next_camp = next(cursor, None)
    return jsonify(next_camp)


# cur_camp = get_items()
# print(cur_camp)
# cur_camp = get_items()
# print(cur_camp)
# cur_camp = get_items()
# print(cur_camp)


info_db = client["results"]
like_collection = info_db["liked_collection"]
dislike_collection = info_db["disliked_collection"]


@app.route("/api/add-item", methods=["POST"])
def add_item():
    data = request.get_json()
    if not data or "title" not in data or "description" not in data:
        return jsonify({"error": "Bro you suck"}), 400

    print("this shows that the data should be parsed")
    if data["liked"]:
        print("hi")

    result = like_collection.insert_one(
        {
            "title": data["title"],
            "description": data["discription"],
            "_id": data["_id"],
            "liked": data["liked"],
        }
    )

    return jsonify({"message": "added", "id": str(results.inserted_id)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

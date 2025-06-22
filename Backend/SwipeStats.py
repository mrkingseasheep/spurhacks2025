from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load MongoDB Atlas URI from .env
load_dotenv()
uri = os.getenv("API_KEY")
client = MongoClient(uri)

# Connect to results db for swipes
results_db = client["results"]
likes_collection = results_db["likes"]
hates_collection = results_db["hates"]

# Connect to ontario_parks db for campsites
parks_db = client["ontario_parks"]
campsites_collection = parks_db["campsites"]

FIELD = "id"  # The field in likes/hates that references the campsite as a string

# Get all liked and hated campsite ids (as strings)
like_ids = [doc[FIELD] for doc in likes_collection.find() if FIELD in doc]
hate_ids = [doc[FIELD] for doc in hates_collection.find() if FIELD in doc]
all_ids = list(set(like_ids + hate_ids))

# Convert string ids to ObjectId for querying campsites
object_ids = [ObjectId(cid) for cid in all_ids]

# Fetch campsite documents from ontario_parks.campsites
campsite_docs = campsites_collection.find({"_id": {"$in": object_ids}})
campsite_data = {str(doc["_id"]): doc for doc in campsite_docs}

# Score: +1 for like, -0.2 for hate
scores = {}
for cid in all_ids:
    score = 0
    if cid in like_ids:
        score += 1
    if cid in hate_ids:
        score -= 0.4
    scores[cid] = score

# Find and print the campsite with the highest score
if scores:
    best_cid = max(scores, key=lambda cid: scores[cid])
    site = campsite_data.get(best_cid)
    if site:
        print("\n⛺ Campsite With Highest Score:\n")
        print({
            "id": best_cid,
            "Provincial Park": site.get("Provincial Park"),
            "Campsite number": site.get("Campsite number"),
            "Photo": site.get("Campsite Photo"),  # Use this field
            "Score": scores[best_cid]
        })

# Find the top 3 campsites with the highest scores
if scores:
    top_3 = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:3]
    print("\n⛺ Top 3 Campsites With Highest Scores:\n")
    for cid, score in top_3:
        site = campsite_data.get(cid)
        if site:
            print({
                "id": cid,
                "Provincial Park": site.get("Provincial Park"),
                "Campsite number": site.get("Campsite number"),
                "Photo": site.get("Campsite Photo"),  # Use this field
                "Score": score
            })

def get_top_campsites(n=2):
    top_n = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:n]
    result = []
    for cid, score in top_n:
        site = campsite_data.get(cid)
        if site:
            result.append({
                "id": cid,
                "Provincial Park": site.get("Provincial Park"),
                "Campsite number": site.get("Campsite number"),
                "Photo": site.get("Campsite Photo"),
                "Score": score
            })
    return result

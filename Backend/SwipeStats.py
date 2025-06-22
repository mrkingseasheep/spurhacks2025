from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

# MongoDB connection
uri = "mongodb+srv://ethanoly:nyCknT3J8fOPwLz0@judgejam.5bpp3ii.mongodb.net/?retryWrites=true&w=majority&appName=JudgeJam"
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["ontario_parks"]
collection = db["campsites"]

# --- Group Preferences (not per person, just two categories) ---
group_preferences = {
    "like": ["68577d8d70302442e5f73ac0", "68577a5370302442e5f739e8"],
    "dislike": ["68577d8d70302442e5f73ac1"]
}

# --- Weights ---
PREFERENCE_WEIGHTS = {
    "like": 1.5,
    "dislike": 0.3
}

# --- Step 1: Gather all unique campsite IDs ---
def get_all_preference_ids(preferences):
    all_ids = set()
    for key in ["like", "dislike"]:
        all_ids.update(preferences.get(key, []))
    return list(all_ids)

def fetch_campsite_docs(ids):
    object_ids = [ObjectId(cid) for cid in ids]
    docs = collection.find({"_id": {"$in": object_ids}})
    return {str(doc["_id"]): doc for doc in docs}

# --- Step 2: Score each campsite ---
def score_campsites(preferences, campsite_data):
    scores = {}
    max_score = 0
    for cid in campsite_data:
        score = 0
        for pref_type, weight in PREFERENCE_WEIGHTS.items():
            if cid in preferences.get(pref_type, []):
                score += weight
        scores[cid] = score
        if score > max_score:
            max_score = score
    return scores, max_score

# --- Step 3: Normalize and rate ---
def rate_campsites(scores, max_score):
    ratings = {}
    for cid, score in scores.items():
        if max_score == 0:
            norm = 0
        else:
            norm = score / max_score
        match_distance = abs(norm - 0.9)
        ratings[cid] = {
            "normalized_score": round(norm, 3),
            "match_distance": round(match_distance, 3)
        }
    return ratings

def pick_best_campsites(ratings, campsite_data, top_n=1):
    # Sort by match_distance (closest to 0.9)
    sorted_sites = sorted(ratings.items(), key=lambda x: x[1]['match_distance'])
    best = []
    for cid, rating in sorted_sites[:top_n]:
        site = campsite_data[cid]
        best.append({
            "id": cid,
            "Provincial Park": site.get("Provincial Park"),
            "Campsite number": site.get("Campsite number"),
            "Score": rating["normalized_score"],
            "Distance from 0.9": rating["match_distance"]
        })
    return best

# --- Main Execution ---
all_ids = get_all_preference_ids(group_preferences)
campsite_data = fetch_campsite_docs(all_ids)
scores, max_score = score_campsites(group_preferences, campsite_data)
ratings = rate_campsites(scores, max_score)

best_campsites = pick_best_campsites(ratings, campsite_data, top_n=3)  # top 3 matches

print("\n🌟 Best Matched Campsites:\n")
for site in best_campsites:
    print(site)

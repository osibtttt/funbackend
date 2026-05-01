from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
import time
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")
HIBP_KEY = os.getenv("HIBP_KEY")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

# IMPORTANT: correct actor format
ACTOR_ID = "eshaan/gaming-xbox-scraper-apify"


# ================= ROBLOX LOOKUP =================
@app.route("/api/roblox/<username>")
def roblox_lookup(username):
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()

        if "data" not in data or not data["data"]:
            return jsonify({"error": "User not found"}), 404

        user = data["data"][0]
        user_id = user["id"]

        profile = requests.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=10).json()
        avatar = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
            f"?userIds={user_id}&size=150x150&format=Png&isCircular=false",
            timeout=10
        ).json()

        return jsonify({
            "username": profile.get("name"),
            "displayName": profile.get("displayName"),
            "userId": user_id,
            "created": profile.get("created"),
            "description": profile.get("description"),
            "avatar": avatar.get("data", [{}])[0].get("imageUrl")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= IP LOOKUP =================
@app.route("/api/ip/<ip>")
def ip_lookup(ip):
    try:
        res = requests.get(
            f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}",
            timeout=10
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= XBOX LOOKUP =================
@app.route("/api/xbox/<gamertag>")
def xbox_lookup(gamertag):
    try:
        if not APIFY_TOKEN:
            return jsonify({"error": "Missing APIFY_TOKEN"}), 500

        # 🔥 FIX: encode actor ID
        encoded_actor = quote(ACTOR_ID, safe='')

        run_url = f"https://api.apify.com/v2/acts/{encoded_actor}/runs?token={APIFY_TOKEN}"

        payload = {
            "gamertag": gamertag
        }

        # Start run
        run_res = requests.post(run_url, json=payload, timeout=15)
        run_data = run_res.json()

        if "data" not in run_data:
            return jsonify({
                "error": "Apify failed",
                "response": run_data
            }), 500

        run_id = run_data["data"]["id"]

        # Wait for completion
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}"

        for _ in range(15):  # ~30 sec max
            status_res = requests.get(status_url, timeout=10).json()
            status = status_res.get("data", {}).get("status")

            if status == "SUCCEEDED":
                dataset_id = status_res["data"]["defaultDatasetId"]
                break

            if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                return jsonify({"error": "Xbox lookup failed"}), 500

            time.sleep(2)
        else:
            return jsonify({"error": "Timeout"}), 504

        # Get results
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
        data = requests.get(dataset_url, timeout=10).json()

        if not data:
            return jsonify({"error": "Gamertag not found"}), 404

        user = data[0]

        return jsonify({
            "Platforms": user.get("Platform(s)"),
            "User Total Gamerscore": user.get("Game Title"),
            "User Name": user.get("User Name"),
            "displayPic": user.get("displayPicRaw"),
            "accountTier": user.get("detail", {}).get("accountTier", "Unknown")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= ENTRYPOINT =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")
HIBP_KEY = os.getenv("HIBP_KEY")


# ================= ROBLOX USER LOOKUP =================
@app.route("/api/roblox/<username>")
def roblox_lookup(username):

    try:
        # Step 1: get user ID
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {
            "usernames": [username],
            "excludeBannedUsers": False
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if not data["data"]:
            return jsonify({"error": "User not found"}), 404

        user = data["data"][0]
        user_id = user["id"]

        # Step 2: profile info
        profile = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()

        # Step 3: avatar
        avatar = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
            f"?userIds={user_id}&size=150x150&format=Png&isCircular=false"
        ).json()

        return jsonify({
            "username": profile.get("name"),
            "displayName": profile.get("displayName"),
            "userId": user_id,
            "created": profile.get("created"),
            "description": profile.get("description"),
            "avatar": avatar["data"][0]["imageUrl"] if avatar.get("data") else None
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= IP OSINT (REAL) =================
@app.route("/api/ip/<ip>")
def ip_lookup(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}")
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= EMAIL BREACH (HIBP) =================
@app.route("/api/breach/<email>")
def breach_lookup(email):
    try:
        headers = {
            "hibp-api-key": HIBP_KEY,
            "user-agent": "OSINT-Hub"
        }

        res = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers
        )

        if res.status_code == 404:
            return jsonify({"breaches": []})

        return jsonify({"breaches": res.json()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= EXISTING XBOX (keep yours) =================
@app.route("/api/xbox/<gamertag>")
def xbox(gamertag):
    url = f"https://xbl.io/api/v2/search/{gamertag}"
    headers = {"X-Authorization": os.getenv("XBOX_KEY")}

    r = requests.get(url, headers=headers)
    data = r.json()

    if "people" not in data or not data["people"]:
        return jsonify({"error": "Not found"}), 404

    user = data["people"][0]

    return jsonify({
        "gamertag": user.get("gamertag"),
        "gamerscore": user.get("gamerScore"),
        "xuid": user.get("xuid"),
        "displayPic": user.get("displayPicRaw")
    })

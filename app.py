from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import re

app = Flask(__name__)
CORS(app)

# ================= ENVIRONMENT VARIABLES =================
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")
HIBP_KEY = os.getenv("HIBP_KEY")
XBOX_KEY = os.getenv("XBOX_KEY")

if not IPINFO_TOKEN:
    print("WARNING: Missing IPINFO_TOKEN")
if not HIBP_KEY:
    print("WARNING: Missing HIBP_KEY")
if not XBOX_KEY:
    print("WARNING: Missing XBOX_KEY")

# ================= AREA CODE LOOKUP =================
AREA_CODE_STATE = { ... your dictionary unchanged ... }

def clean_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    return digits

def validate_phone(phone):
    digits = clean_phone(phone)
    return len(digits) == 10 and digits[:3] in AREA_CODE_STATE

def get_state_from_phone(phone):
    digits = clean_phone(phone)
    if len(digits) == 10:
        return AREA_CODE_STATE.get(digits[:3])
    return None

def validate_email(email):
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email))

# ================= ROBLOX LOOKUP =================
@app.route("/api/roblox/<username>")
def roblox_lookup(username):
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        res = requests.post(url, json=payload)
        data = res.json()

        if "data" not in data or not data["data"]:
            return jsonify({"error": "User not found"}), 404

        user = data["data"][0]
        user_id = user["id"]

        profile = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
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
            "avatar": avatar.get("data", [{}])[0].get("imageUrl")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= IP LOOKUP =================
@app.route("/api/ip/<ip>")
def ip_lookup(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}")
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= PHONE LOOKUP =================
@app.route("/api/phone")
def phone_lookup():
    phone = request.args.get("number", "").strip()

    if not phone:
        return jsonify({"error": "No phone number provided"}), 400

    if not validate_phone(phone):
        return jsonify({"error": "Invalid phone number"}), 400

    cleaned = clean_phone(phone)
    state = get_state_from_phone(cleaned)

    return jsonify({
        "number": cleaned,
        "valid": True,
        "state": state or "Unknown",
        "country": "United States" if state else "Unknown"
    })

# ================= EMAIL BREACH LOOKUP =================
@app.route("/api/breach/<email>")
def breach_lookup(email):
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        headers = {
            "hibp-api-key": HIBP_KEY,
            "user-agent": "OSINT-Hub",
            "Add-Padding": "true"
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

# ================= XBOX LOOKUP =================
@app.route("/api/xbox/<gamertag>")
def xbox_lookup(gamertag):
    try:
        url = f"https://xbl.io/api/v2/search/{gamertag}"
        headers = {"X-Authorization": XBOX_KEY}
        r = requests.get(url, headers=headers)
        data = r.json()

        if "people" not in data or not data["people"]:
            return jsonify({"error": "Gamertag not found"}), 404

        user = data["people"][0]

        return jsonify({
            "gamertag": user.get("gamertag"),
            "gamerscore": user.get("gamerScore"),
            "xuid": user.get("xuid"),
            "reputation": user.get("xboxOneRep", "Unknown"),
            "displayPic": user.get("displayPicRaw")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= ENTRYPOINT =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

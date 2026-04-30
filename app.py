from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# ENV VARIABLES (set these in Render dashboard)
XBOX_API_KEY = os.getenv("XBOX_API_KEY")
NUMVERIFY_KEY = os.getenv("NUMVERIFY_KEY")

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "OSINT Backend Running"}

# =========================
# XBOX LOOKUP
# =========================
@app.route("/api/xbox/<gamertag>")
def xbox_lookup(gamertag):
    try:
        url = f"https://xbl.io/api/v2/search/{gamertag}"
        headers = {"X-Authorization": XBOX_API_KEY}

        res = requests.get(url, headers=headers)

        if res.status_code != 200:
            return jsonify({"error": "Xbox API failed"}), 500

        data = res.json()

        if "people" not in data or not data["people"]:
            return jsonify({"error": "Gamertag not found"}), 404

        user = data["people"][0]

        return jsonify({
            "gamertag": user.get("gamertag"),
            "gamerscore": user.get("gamerScore"),
            "xuid": user.get("xuid"),
            "reputation": user.get("xboxOneRep"),
            "displayPic": user.get("displayPicRaw")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# PHONE LOOKUP
# =========================
@app.route("/api/phone")
def phone_lookup():
    number = request.args.get("number")

    if not number:
        return jsonify({"error": "Missing number"}), 400

    try:
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={number}"
        res = requests.get(url)
        data = res.json()

        return jsonify({
            "valid": data.get("valid"),
            "country_name": data.get("country_name"),
            "carrier": data.get("carrier"),
            "location": data.get("location")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# EMAIL (basic placeholder)
# =========================
@app.route("/api/email")
def email_lookup():
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "Missing email"}), 400

    # You can later connect HaveIBeenPwned or similar
    return jsonify({
        "breaches": [],
        "note": "No breach API connected yet"
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

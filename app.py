from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ================= ENV VARS =================
NUMVERIFY_KEY = os.environ.get("NUMVERIFY_KEY")
XBL_API_KEY = os.environ.get("XBL_API_KEY")

# ================= HOME =================
@app.route("/")
def home():
    return "OSINT Backend Running"

# ================= XBOX =================
@app.route("/api/xbox/<gamertag>")
def xbox_lookup(gamertag):
    url = f"https://xbl.io/api/v2/search/{gamertag}"

    headers = {
        "X-Authorization": XBL_API_KEY
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)

        if res.status_code != 200:
            return jsonify({
                "error": "Failed to fetch data",
                "status": res.status_code
            }), 500

        data = res.json()

        if "people" not in data or len(data["people"]) == 0:
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


# ================= PHONE =================
@app.route("/api/phone")
def phone_lookup():
    number = request.args.get("number")

    if not number:
        return jsonify({"error": "Missing phone number"}), 400

    try:
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={number}"
        res = requests.get(url, timeout=5)
        return jsonify(res.json())

    except:
        return jsonify({"error": "Phone lookup failed"}), 500


# ================= EMAIL (HIBP) =================
@app.route("/api/email")
def email_lookup():
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "Missing email"}), 400

    try:
        res = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={"User-Agent": "OSINT-Hub"},
            timeout=5
        )

        if res.status_code == 404:
            return jsonify({"breaches": []})

        return jsonify({"breaches": res.json()})

    except:
        return jsonify({"error": "Email lookup failed"}), 500


# ================= START =================
if __name__ == "__main__":
    app.run()

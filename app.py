from flask import Flask, jsonify, request
from flask_cors import CORS  # Add this for CORS support
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ENV VARIABLES (set these in Render dashboard)
XBOX_API_KEY = os.getenv("XBOX_API_KEY")
NUMVERIFY_KEY = os.getenv("NUMVERIFY_KEY")

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return jsonify({"status": "OSINT Backend Running"})  # Added jsonify

# =========================
# XBOX LOOKUP
# =========================
@app.route("/api/xbox/<gamertag>")
def xbox_lookup(gamertag):
    # Check if API key is configured
    if not XBOX_API_KEY:
        return jsonify({"error": "Xbox API key not configured"}), 500
    
    try:
        url = f"https://xbl.io/api/v2/search/{gamertag}"
        headers = {"X-Authorization": XBOX_API_KEY}

        res = requests.get(url, headers=headers, timeout=10)  # Added timeout

        if res.status_code != 200:
            return jsonify({"error": f"Xbox API failed with status {res.status_code}"}), 500

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

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# PHONE LOOKUP
# =========================
@app.route("/api/phone")
def phone_lookup():
    # Check if API key is configured
    if not NUMVERIFY_KEY:
        return jsonify({"error": "Numverify API key not configured"}), 500
    
    number = request.args.get("number")

    if not number:
        return jsonify({"error": "Missing number parameter"}), 400

    try:
        # Clean the number (remove spaces, dashes, etc.)
        clean_number = ''.join(filter(str.isdigit, number))
        
        url = f"http://apilayer.net/api/validate"
        params = {
            "access_key": NUMVERIFY_KEY,
            "number": clean_number
        }
        
        res = requests.get(url, params=params, timeout=10)  # Use params instead of string concatenation
        
        if res.status_code != 200:
            return jsonify({"error": f"Phone API failed with status {res.status_code}"}), 500
            
        data = res.json()

        # Check for API errors
        if "error" in data:
            return jsonify({"error": data["error"].get("info", "Phone API error")}), 400

        return jsonify({
            "valid": data.get("valid", False),
            "country_name": data.get("country_name"),
            "carrier": data.get("carrier"),
            "location": data.get("location"),
            "country_code": data.get("country_code"),
            "line_type": data.get("line_type")
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# EMAIL (basic placeholder)
# =========================
@app.route("/api/email")
def email_lookup():
    email = request.args.get("email")

    if not email:
        return jsonify({"error": "Missing email parameter"}), 400
    
    # Basic email validation
    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # You can later connect HaveIBeenPwned or similar
    return jsonify({
        "email": email,
        "breaches": [],
        "note": "No breach API connected yet"
    })

# =========================
# HEALTH CHECK (for Render)
# =========================
@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

# =========================
# ERROR HANDLERS
# =========================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use PORT env var for Render
    app.run(host="0.0.0.0", port=port, debug=False)  # Set debug=False in production

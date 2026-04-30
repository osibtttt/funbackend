
Copy

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import re
 
app = Flask(__name__)
CORS(app)
 
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")
HIBP_KEY = os.getenv("HIBP_KEY")
XBOX_KEY = os.getenv("XBOX_KEY")
 
# ================= AREA CODE -> STATE LOOKUP =================
AREA_CODE_STATE = {
    "201": "New Jersey", "202": "Washington D.C.", "203": "Connecticut",
    "205": "Alabama", "206": "Washington", "207": "Maine",
    "208": "Idaho", "209": "California", "210": "Texas",
    "212": "New York", "213": "California", "214": "Texas",
    "215": "Pennsylvania", "216": "Ohio", "217": "Illinois",
    "218": "Minnesota", "219": "Indiana", "220": "Ohio",
    "224": "Illinois", "225": "Louisiana", "228": "Mississippi",
    "229": "Georgia", "231": "Michigan", "234": "Ohio",
    "239": "Florida", "240": "Maryland", "248": "Michigan",
    "251": "Alabama", "252": "North Carolina", "253": "Washington",
    "254": "Texas", "256": "Alabama", "260": "Indiana",
    "262": "Wisconsin", "267": "Pennsylvania", "269": "Michigan",
    "270": "Kentucky", "272": "Pennsylvania", "276": "Virginia",
    "281": "Texas", "301": "Maryland", "302": "Delaware",
    "303": "Colorado", "304": "West Virginia", "305": "Florida",
    "307": "Wyoming", "308": "Nebraska", "309": "Illinois",
    "310": "California", "312": "Illinois", "313": "Michigan",
    "314": "Missouri", "315": "New York", "316": "Kansas",
    "317": "Indiana", "318": "Louisiana", "319": "Iowa",
    "320": "Minnesota", "321": "Florida", "323": "California",
    "325": "Texas", "330": "Ohio", "331": "Illinois",
    "334": "Alabama", "336": "North Carolina", "337": "Louisiana",
    "339": "Massachusetts", "340": "U.S. Virgin Islands",
    "341": "California", "346": "Texas", "347": "New York",
    "351": "Massachusetts", "352": "Florida", "360": "Washington",
    "361": "Texas", "364": "Kentucky", "380": "Ohio",
    "385": "Utah", "386": "Florida", "401": "Rhode Island",
    "402": "Nebraska", "404": "Georgia", "405": "Oklahoma",
    "406": "Montana", "407": "Florida", "408": "California",
    "409": "Texas", "410": "Maryland", "412": "Pennsylvania",
    "413": "Massachusetts", "414": "Wisconsin", "415": "California",
    "417": "Missouri", "419": "Ohio", "423": "Tennessee",
    "424": "California", "425": "Washington", "430": "Texas",
    "432": "Texas", "434": "Virginia", "435": "Utah",
    "440": "Ohio", "442": "California", "443": "Maryland",
    "447": "Illinois", "458": "Oregon", "463": "Indiana",
    "469": "Texas", "470": "Georgia", "475": "Connecticut",
    "478": "Georgia", "479": "Arkansas", "480": "Arizona",
    "484": "Pennsylvania", "501": "Arkansas", "502": "Kentucky",
    "503": "Oregon", "504": "Louisiana", "505": "New Mexico",
    "507": "Minnesota", "508": "Massachusetts", "509": "Washington",
    "510": "California", "512": "Texas", "513": "Ohio",
    "515": "Iowa", "516": "New York", "517": "Michigan",
    "518": "New York", "520": "Arizona", "530": "California",
    "531": "Nebraska", "534": "Wisconsin", "539": "Oklahoma",
    "540": "Virginia", "541": "Oregon", "551": "New Jersey",
    "559": "California", "561": "Florida", "562": "California",
    "563": "Iowa", "564": "Washington", "567": "Ohio",
    "570": "Pennsylvania", "571": "Virginia", "573": "Missouri",
    "574": "Indiana", "575": "New Mexico", "580": "Oklahoma",
    "585": "New York", "586": "Michigan", "601": "Mississippi",
    "602": "Arizona", "603": "New Hampshire", "605": "South Dakota",
    "606": "Kentucky", "607": "New York", "608": "Wisconsin",
    "609": "New Jersey", "610": "Pennsylvania", "612": "Minnesota",
    "614": "Ohio", "615": "Tennessee", "616": "Michigan",
    "617": "Massachusetts", "618": "Illinois", "619": "California",
    "620": "Kansas", "623": "Arizona", "626": "California",
    "628": "California", "629": "Tennessee", "630": "Illinois",
    "631": "New York", "636": "Missouri", "641": "Iowa",
    "646": "New York", "650": "California", "651": "Minnesota",
    "657": "California", "659": "Alabama", "660": "Missouri",
    "661": "California", "662": "Mississippi", "667": "Maryland",
    "669": "California", "671": "Guam", "678": "Georgia",
    "680": "New York", "681": "West Virginia", "682": "Texas",
    "689": "Florida", "701": "North Dakota", "702": "Nevada",
    "703": "Virginia", "704": "North Carolina", "706": "Georgia",
    "707": "California", "708": "Illinois", "712": "Iowa",
    "713": "Texas", "714": "California", "715": "Wisconsin",
    "716": "New York", "717": "Pennsylvania", "718": "New York",
    "719": "Colorado", "720": "Colorado", "724": "Pennsylvania",
    "725": "Nevada", "727": "Florida", "730": "Illinois",
    "731": "Tennessee", "732": "New Jersey", "734": "Michigan",
    "737": "Texas", "740": "Ohio", "743": "North Carolina",
    "747": "California", "754": "Florida", "757": "Virginia",
    "760": "California", "762": "Georgia", "763": "Minnesota",
    "765": "Indiana", "769": "Mississippi", "770": "Georgia",
    "772": "Florida", "773": "Illinois", "774": "Massachusetts",
    "775": "Nevada", "779": "Illinois", "781": "Massachusetts",
    "785": "Kansas", "786": "Florida", "787": "Puerto Rico",
    "801": "Utah", "802": "Vermont", "803": "South Carolina",
    "804": "Virginia", "805": "California", "806": "Texas",
    "808": "Hawaii", "810": "Michigan", "812": "Indiana",
    "813": "Florida", "814": "Pennsylvania", "815": "Illinois",
    "816": "Missouri", "817": "Texas", "818": "California",
    "820": "California", "828": "North Carolina", "830": "Texas",
    "831": "California", "832": "Texas", "835": "Pennsylvania",
    "843": "South Carolina", "845": "New York", "847": "Illinois",
    "848": "New Jersey", "850": "Florida", "854": "South Carolina",
    "856": "New Jersey", "857": "Massachusetts", "858": "California",
    "859": "Kentucky", "860": "Connecticut", "862": "New Jersey",
    "863": "Florida", "864": "South Carolina", "865": "Tennessee",
    "870": "Arkansas", "872": "Illinois", "878": "Pennsylvania",
    "901": "Tennessee", "903": "Texas", "904": "Florida",
    "906": "Michigan", "907": "Alaska", "908": "New Jersey",
    "909": "California", "910": "North Carolina", "912": "Georgia",
    "913": "Kansas", "914": "New York", "915": "Texas",
    "916": "California", "917": "New York", "918": "Oklahoma",
    "919": "North Carolina", "920": "Wisconsin", "925": "California",
    "928": "Arizona", "929": "New York", "930": "Indiana",
    "931": "Tennessee", "934": "New York", "936": "Texas",
    "937": "Ohio", "938": "Alabama", "940": "Texas",
    "941": "Florida", "945": "Texas", "947": "Michigan",
    "949": "California", "951": "California", "952": "Minnesota",
    "954": "Florida", "956": "Texas", "959": "Connecticut",
    "970": "Colorado", "971": "Oregon", "972": "Texas",
    "973": "New Jersey", "975": "Missouri", "978": "Massachusetts",
    "979": "Texas", "980": "North Carolina", "984": "North Carolina",
    "985": "Louisiana", "986": "Idaho", "989": "Michigan",
}
 
def get_state_from_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('1') and len(digits) == 11:
        digits = digits[1:]
    if len(digits) >= 10:
        area = digits[:3]
        return AREA_CODE_STATE.get(area)
    return None
 
def validate_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('1'):
        digits = digits[1:]
    return len(digits) == 10
 
def validate_email(email):
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email))
 
# ================= ROBLOX USER LOOKUP =================
@app.route("/api/roblox/<username>")
def roblox_lookup(username):
    try:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        res = requests.post(url, json=payload)
        data = res.json()
 
        if not data.get("data"):
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
            "avatar": avatar["data"][0]["imageUrl"] if avatar.get("data") else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# ================= IP OSINT =================
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
        return jsonify({"error": "Invalid phone number format. Please enter a 10-digit US number."}), 400
 
    state = get_state_from_phone(phone)
 
    return jsonify({
        "number": phone,
        "valid": True,
        "state": state or "Unknown",
        "country": "United States" if state else "Unknown",
    })
 
# ================= EMAIL BREACH (HIBP) =================
@app.route("/api/breach/<email>")
def breach_lookup(email):
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400
 
    try:
        headers = {"hibp-api-key": HIBP_KEY, "user-agent": "OSINT-Hub"}
        res = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers
        )
        if res.status_code == 404:
            return jsonify({"breaches": []})
        return jsonify({"breaches": res.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# ================= XBOX =================
@app.route("/api/xbox/<gamertag>")
def xbox(gamertag):
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
        return jsonify({"error": "Xbox lookup failed"}), 500
 
if __name__ == "__main__":
    app.run(debug=True)

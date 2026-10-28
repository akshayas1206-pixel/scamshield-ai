from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

SCAM_PATTERNS = [
    (r"\b(urgent|immediately|act now|last chance|within \d+ hours?)\b", "Urgent or high-pressure language"),
    (r"\b(password|otp|one[- ]time password|pin|cvv|bank details|login details)\b", "Request for sensitive information"),
    (r"\b(prize|lottery|winner|won money|claim your reward|free gift)\b", "Unexpected prize or reward"),
    (r"\b(transfer money|send money|pay now|processing fee|gift card|crypto|cryptocurrency)\b", "Request for money or unusual payment"),
    (r"\b(account (will be|has been) (blocked|suspended)|verify your account)\b", "Account threat or verification pressure"),
    (r"\b(click here|open this link|verify now|download this file)\b", "Prompt to click a link or download a file"),
]

def analyze_message(message):
    matches = []
    for pattern, reason in SCAM_PATTERNS:
        if re.search(pattern, message, flags=re.IGNORECASE):
            matches.append(reason)
    score = min(95, len(matches) * 22)
    if re.search(r"https?://|www\.", message, re.IGNORECASE):
        score = min(98, score + 12)
        matches.append("Contains a web link")
    if not message.strip():
        return {"score": 0, "level": "No message", "reasons": ["Paste a message to analyze."],
                "advice": "Enter a message first."}
    if score >= 60:
        level = "High risk"
        advice = "Do not click links or share codes, passwords, or payment details. Verify using an official contact method."
    elif score >= 25:
        level = "Caution"
        advice = "Be careful. Check the sender and verify any request independently before acting."
    else:
        level = "Lower risk based on these checks"
        advice = "No common warning patterns were detected, but this does not prove the message is safe."
    if not matches:
        matches = ["No common warning patterns detected by this basic prototype"]
    return {"score": score, "level": level, "reasons": matches, "advice": advice}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", ""))[:10000]
    return jsonify(analyze_message(message))

@app.route("/api/check-url", methods=["POST"])
def check_url():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", "")).strip()
    reasons = []
    if not url:
        return jsonify({"level": "No URL", "reasons": ["Enter a URL to check."]})
    if not re.match(r"^https?://", url, re.IGNORECASE):
        reasons.append("The address does not start with http:// or https://")
    if re.search(r"@", url):
        reasons.append("The address contains @, which can sometimes disguise the destination")
    if re.search(r"\b(bit\.ly|tinyurl\.com|t\.co|shorturl\.at)\b", url, re.IGNORECASE):
        reasons.append("This appears to use a shortened link")
    if re.search(r"\d{5,}", url):
        reasons.append("The address contains a long number sequence")
    if re.search(r"(login|verify|wallet|claim|secure|account)", url, re.IGNORECASE):
        reasons.append("The address uses a word often seen in account or verification links")
    if reasons:
        level = "Needs caution"
    else:
        level = "No obvious pattern detected"
        reasons.append("Basic checks found no obvious warning pattern. This does not prove the URL is safe.")
    return jsonify({"level": level, "reasons": reasons})

if __name__ == "__main__":
    app.run(debug=True)

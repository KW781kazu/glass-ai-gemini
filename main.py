from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    from_number = request.form.get("From", "不明")

    prompt = f"{from_number} さんから電話がありました。お名前を聞いてください。"

    gemini_api = os.environ.get("GEMINI_API_KEY")
    headers = {
        "Authorization": f"Bearer {gemini_api}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        gemini_response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers=headers,
            json=payload,
            timeout=10
        )
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "こんにちは。こちらはAI受付です。お名前を教えてください。"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Pause length="5"/>
  <Say voice="alice" language="ja-JP">お名前をお願いします。</Say>
</Response>"""

    return Response(twiml, mimetype="text/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    host = "0.0.0.0"
    app.run(host=host, port=port)

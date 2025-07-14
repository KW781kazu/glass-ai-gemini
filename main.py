
from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    from_number = request.form.get("From", "不明")

    # Geminiに送るプロンプト（お客様に話しかける内容を指示）
    prompt = f"{from_number} さんから電話がありました。お名前を聞いてください。"

    # Gemini APIに送信
    headers = {
        "Authorization": f"Bearer {os.environ['GEMINI_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    gemini_response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json=payload
    )

    try:
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "こんにちは。こちらはAI受付です。お名前を教えてください。"

    # Twilioに返すTwiML（日本語で話す）
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
</Response>"""

    return Response(twiml, mimetype="text/xml")

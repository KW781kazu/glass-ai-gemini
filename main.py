from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # 発話後、音声認識を待つ
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" timeout="5" speechTimeout="auto" action="/handle-name" method="POST">
    <Say language="ja-JP" voice="alice">こんにちは。お名前を教えてください。</Say>
  </Gather>
</Response>"""
    return Response(response, mimetype="text/xml")


@app.route("/handle-name", methods=["POST"])
def handle_name():
    user_input = request.form.get("SpeechResult", "不明")
    prompt = f"お客様が「{user_input}」と答えました。ていねいに挨拶してください。"

    # Gemini に問い合わせ
    headers = {
        "Authorization": f"Bearer {os.environ['GEMINI_API_KEY']}",
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
            timeout=5
        )
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "ありがとうございます。受付を完了しました。"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="ja-JP" voice="alice">{reply}</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

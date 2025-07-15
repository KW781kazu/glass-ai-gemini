from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    from_number = request.form.get("From", "不明")

    # Gemini に送るプロンプト
    prompt = f"{from_number} さんから電話がありました。お名前を聞いてください。"

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
            timeout=5  # タイムアウトを設定
        )
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "こんにちは。こちらはAI受付です。お名前を教えてください。"

    # TwiML 応答を生成
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
</Response>"""

    return Response(twiml, mimetype="text/xml")

if __name__ == "__main__":
    # ポイント：Render で正しく外部公開するために必要
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

# 通話の最初に呼ばれるルート
@app.route("/incoming-call", methods=["POST"])
def handle_call():
    from_number = request.form.get("From", "不明")

    # Gemini に送るプロンプト
    prompt = f"{from_number} さんから電話がありました。お名前を聞いてください。"

    # Gemini へ送信
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

    # TwiML で返す（ここで音声認識の入力を受け付ける）
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" timeout="5" language="ja-JP"
          action="https://glass-ai-gemini.onrender.com/process-name" method="POST">
    <Say voice="alice" language="ja-JP">{reply}</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">失礼しました。もう一度おかけ直しください。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# 名前を処理するルート
@app.route("/process-name", methods=["POST"])
def process_name():
    name = request.form.get("SpeechResult", "名前が聞き取れませんでした")
    print(f"📞 音声認識結果: {name}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{name}さんですね。ありがとうございます。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# Renderのヘルスチェック用ルート（optional）
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

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
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
        headers=headers,
        json=payload
    )

    try:
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "こんにちは。こちらはAI受付です。お名前を教えてください。"

    # Twilioに返すTwiML（<Gather>で音声を受け取る準備をする）
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" timeout="5" language="ja-JP" action="/process-name" method="POST">
    <Say voice="alice" language="ja-JP">{reply}</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">失礼しました。もう一度おかけ直しください。</Say>
</Response>"""

    return Response(twiml, mimetype="text/xml")

# 名前処理ルート（仮）
@app.route("/process-name", methods=["POST"])
def process_name():
    speech_result = request.form.get("SpeechResult", "聞き取れませんでした")
    reply = f"{speech_result}さんですね。ありがとうございます。担当者におつなぎします。"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# Flask 起動設定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

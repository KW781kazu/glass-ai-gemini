from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # 初回の挨拶と名前を聞く
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" language="ja-JP" action="/handle-speech" method="POST">
    <Say voice="alice" language="ja-JP">こんにちは。お名前を教えてください。</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">音声が聞き取れませんでした。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")


@app.route("/handle-speech", methods=["POST"])
def handle_speech():
    # ユーザーの発話を取得
    user_speech = request.form.get("SpeechResult", "わかりません")

    # Geminiにプロンプトとして送る
    prompt = f"相手が「{user_speech}」と話しました。それに対して自然な日本語で返答してください。"

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
            json=payload
        )
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply = "ありがとうございます。担当者におつなぎします。"

    # 応答をTwilioへ返す
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Say voice="alice" language="ja-JP">それでは失礼いたします。</Say>
  <Hangup/>
</Response>"""

    return Response(twiml, mimetype="text/xml")

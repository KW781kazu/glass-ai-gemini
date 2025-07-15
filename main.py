from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

# 最初の通話受付（名前を聞く）
@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" timeout="10" speechTimeout="auto" action="/handle-name" method="POST">
    <Say language="ja-JP" voice="alice">こんにちは。お名前を教えてください。</Say>
  </Gather>
  <Say language="ja-JP" voice="alice">音声が確認できませんでした。もう一度おかけ直しください。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# ユーザーが名前を答えたあとの処理
@app.route("/handle-name", methods=["POST"])
def handle_name():
    # Twilioからの音声認識結果
    user_input = request.form.get("SpeechResult", "不明")

    # Geminiへ送信するプロンプト
    prompt = f"お客様の名前は「{user_input}」です。丁寧にお礼を伝えてください。"

    # Gemini API 呼び出し
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
    except Exception as e:
        reply = "ありがとうございます。担当者におつなぎします。"

    # Twilioへ返すTwiML（日本語で応答）
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="ja-JP" voice="alice">{reply}</Say>
  <Pause length="1"/>
  <Say language="ja-JP" voice="alice">それでは失礼いたします。</Say>
  <Hangup/>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# ポート指定（Render用）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

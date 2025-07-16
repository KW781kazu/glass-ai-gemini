from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    # 最初の着信に対して、音声入力を促す
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" timeout="5" speechTimeout="auto" action="/process-name" method="POST">
    <Say voice="alice" language="ja-JP">こんにちは。こちらはAI受付です。お名前を教えてください。</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">すみません、音声が認識できませんでした。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

@app.route("/process-name", methods=["POST"])
def process_name():
    # Twilioから音声認識結果を取得
    name = request.form.get("SpeechResult", "").strip()
    if not name:
        reply = "すみません、うまく聞き取れませんでした。もう一度おかけ直しください。"
    else:
        # Gemini APIで応答生成
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            reply = "Gemini APIキーが設定されていません。"
        else:
            headers = {
                "Authorization": f"Bearer {gemini_api_key}",
                "Content-Type": "application/json"
            }
            prompt = f"お客様のお名前は {name} さんです。確認してお礼を伝えてください。"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }

            try:
                res = requests.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                    headers=headers,
                    json=payload,
                    timeout=5
                )
                reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                reply = f"{name}さん、ありがとうございます。担当者におつなぎします。"

    # 応答を読み上げ、通話を終了
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Say voice="alice" language="ja-JP">それでは失礼いたします。</Say>
  <Hangup/>
</Response>"""
    return Response(twiml, mimetype="text/xml")

# ポート設定（Render環境用）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

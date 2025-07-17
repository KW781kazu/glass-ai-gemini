from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # 最初の案内：名前を聞く
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/gather" method="POST" timeout="5">
    <Say voice="alice" language="ja-JP">こんにちは。こちらはAI受付です。お名前を教えてください。</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">うまく聞き取れませんでした。もう一度お願いします。</Say>
</Response>"""
    return Response(twiml, mimetype="text/xml")

@app.route("/gather", methods=["POST"])
def gather():
    user_speech = request.form.get("SpeechResult", "")
    print("📞 ユーザー発話:", user_speech)

    if not user_speech:
        reply = "すみません、もう一度お名前を教えてください。"
    else:
        prompt = f"お客様は「{user_speech}」と話しました。名前として理解し、「{user_speech}さんですね。ありがとうございます。」という日本語で返してください。"

        headers = {
            "Authorization": f"Bearer {os.environ['GEMINI_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=payload
            )
            reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("Gemini API error:", e)
            reply = "エラーが発生しました。もう一度お話ください。"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Say voice="alice" language="ja-JP">それでは失礼いたします。</Say>
  <Hangup/>
</Response>"""
    return Response(twiml, mimetype="text/xml")

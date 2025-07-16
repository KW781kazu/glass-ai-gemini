from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    # 初回の挨拶と音声認識のための Gather を返す
    response = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Gather input="speech" action="/handle-name" method="POST" language="ja-JP" timeout="5">
            <Say voice="alice" language="ja-JP">こんにちは。こちらはAI受付です。お名前を教えてください。</Say>
        </Gather>
        <Say voice="alice" language="ja-JP">すみません、お名前を認識できませんでした。</Say>
        <Hangup/>
    </Response>
    """
    return Response(response, mimetype="text/xml")

@app.route("/handle-name", methods=["POST"])
def handle_name():
    # Twilioが認識した音声のテキストを取得
    user_name = request.form.get("SpeechResult", "").strip()

    if user_name:
        # Geminiに問い合わせ（オプション）
        prompt = f"お客様の名前は「{user_name}」です。丁寧に感謝して、担当者につなぐ案内をしてください。"
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
            reply = f"{user_name}さん、ありがとうございます。担当者におつなぎします。"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ja-JP">{reply}</Say>
    <Say voice="alice" language="ja-JP">それでは失礼いたします。</Say>
    <Hangup/>
</Response>
"""
    else:
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ja-JP">すみません、認識できませんでした。もう一度お電話ください。</Say>
    <Hangup/>
</Response>
"""
    return Response(twiml, mimetype="text/xml")

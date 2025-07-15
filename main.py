from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    # 音声認識の結果がある場合
    speech_result = request.form.get("SpeechResult")
    from_number = request.form.get("From", "不明")

    if speech_result:
        # ユーザーが話した内容をGeminiに送信
        prompt = f"お客様が「{speech_result}」と言いました。それに自然に返答してください。"
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
            reply = "うまく聞き取れませんでした。もう一度お願いします。"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Hangup/>
</Response>"""

        return Response(twiml, mimetype="text/xml")

    else:
        # 最初の音声入力を待つ
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">こんにちは。お名前を教えてください。</Say>
  <Gather input="speech" action="/incoming-call" method="POST" language="ja-JP" timeout="5"/>
</Response>"""
        return Response(twiml, mimetype="text/xml")

# Renderの場合は以下を追加
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

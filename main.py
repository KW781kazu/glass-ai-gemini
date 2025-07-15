from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["POST"])
def handle_call():
    speech_result = request.form.get("SpeechResult")
    from_number = request.form.get("From", "不明")

    if speech_result:
        print(f"[受信した発話] {speech_result}")
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
            print("[Geminiレスポンス]", gemini_response.text)  # 追加
            reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print("[Geminiエラー]", str(e))  # 追加
            reply = "うまく聞き取れませんでした。もう一度お願いします。"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Hangup/>
</Response>"""
        return Response(twiml, mimetype="text/xml")

    else:
        # 最初の応答（音声をGather）
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">こんにちは。お名前を教えてください。</Say>
  <Gather input="speech" action="/incoming-call" method="POST" language="ja-JP" timeout="5" />
</Response>"""
        return Response(twiml, mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

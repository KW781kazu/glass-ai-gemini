from flask import Flask, request, Response
import os
import requests

app = Flask(__name__)

@app.route("/incoming-call", methods=["GET", "POST"])
def handle_call():
    speech_result = request.form.get("SpeechResult")
    from_number = request.form.get("From", "不明")

    print(f"[SpeechResult] {speech_result}")
    print(f"[From] {from_number}")

    if speech_result is None:
        # 初回アクセス時（まだ発話されていない）
        print("[INFO] 初回の案内を再生中")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="/incoming-call" method="POST" language="ja-JP" timeout="10" speechTimeout="auto">
    <Say voice="alice" language="ja-JP">こんにちは。お名前を教えてください。</Say>
  </Gather>
  <Say voice="alice" language="ja-JP">音声が確認できませんでした。</Say>
</Response>"""
        return Response(twiml, mimetype="text/xml")

    # 発話結果が空または認識できなかった場合
    if not speech_result.strip():
        print("[WARN] SpeechResult が空または無効です")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">うまく聞き取れませんでした。もう一度お願いします。</Say>
  <Pause length="1" />
  <Hangup />
</Response>"""
        return Response(twiml, mimetype="text/xml")

    # Gemini に送信するプロンプト
    prompt = f"{from_number} さんから電話がありました。相手の名前は {speech_result} です。最後に「ありがとうございます。担当者におつなぎします。それでは失礼いたします」と言ってください。"

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
        print(f"[Gemini Raw Response] {gemini_response.text}")
        reply = gemini_response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[ERROR] Gemini API failed: {e}")
        reply = "ありがとうございます。担当者におつなぎします。それでは失礼いたします。"

    # Twilio に返す応答
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice" language="ja-JP">{reply}</Say>
  <Hangup />
</Response>"""
    return Response(twiml, mimetype="text/xml")

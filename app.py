import os
import requests
from flask import Flask, request, send_file
from gtts import gTTS

# إعداد القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # توكن البوت
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي

if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

def set_webhook():
    """إعداد Webhook للبوت."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Webhook تم إعداده بنجاح: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في إعداد Webhook: {e}")

def send_message(chat_id, text):
    """إرسال رسالة نصية إلى المستخدم."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ أثناء إرسال الرسالة: {e}")

def send_audio(chat_id, audio_path):
    """إرسال ملف صوتي إلى المستخدم."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendAudio"
    with open(audio_path, "rb") as audio_file:
        payload = {"chat_id": chat_id}
        files = {"audio": audio_file}
        try:
            requests.post(url, data=payload, files=files)
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ أثناء إرسال الملف الصوتي: {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """التعامل مع الرسائل الواردة من Telegram."""
    data = request.get_json()

    if not data or "message" not in data:
        return "No message data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.lower() == "/start":
        send_message(chat_id, "مرحبًا! أرسل لي أي نص لتحويله إلى صوت.")
    elif text:
        try:
            tts = gTTS(text, lang="ar")
            audio_path = f"{chat_id}_audio.mp3"
            tts.save(audio_path)
            send_audio(chat_id, audio_path)
            os.remove(audio_path)
        except Exception as e:
            send_message(chat_id, f"❌ خطأ أثناء تحويل النص إلى صوت: {e}")
    else:
        send_message(chat_id, "❌ الرجاء إرسال نص صحيح.")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)

import os
import requests
from flask import Flask, request, jsonify
from gtts import gTTS
from tempfile import NamedTemporaryFile

# إعداد القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # توكن البوت
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي

if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

# إعداد اللغات المدعومة
LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "fr": "Français",
    "es": "Español",
}

DEFAULT_LANGUAGE = "ar"

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
        raise

def send_message(chat_id, text):
    """إرسال رسالة نصية إلى المستخدم."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ أثناء إرسال الرسالة: {e}")

def send_audio(chat_id, audio_file):
    """إرسال ملف صوتي إلى المستخدم."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendAudio"
    try:
        with open(audio_file.name, "rb") as f:
            response = requests.post(url, data={"chat_id": chat_id}, files={"audio": f})
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ أثناء إرسال الملف الصوتي: {e}")

def synthesize_speech(text, lang=DEFAULT_LANGUAGE):
    """تحويل النص إلى صوت باستخدام gTTS."""
    try:
        tts = gTTS(text=text, lang=lang)
        temp_audio = NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)
        return temp_audio
    except Exception as e:
        print(f"❌ خطأ أثناء تحويل النص إلى صوت: {e}")
        raise

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """التعامل مع الرسائل الواردة من Telegram."""
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message data"}), 400

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text.lower() == "/start":
        send_message(
            chat_id,
            "✨ *مرحبًا بك في بوت تحويل النص إلى صوت!*\n\n"
            "💬 أرسل النص الذي ترغب في تحويله إلى صوت.\n\n"
            "🌐 *اللغات المدعومة:*\n" +
            "\n".join([f"- `{key}`: {value}" for key, value in LANGUAGES.items()]) +
            "\n\n⚙️ *الأوامر:*\n"
            "`/lang [رمز اللغة]` - لتغيير اللغة.\n"
        )
        return jsonify({"status": "ok"}), 200

    elif text.startswith("/lang"):
        try:
            _, lang = text.split(maxsplit=1)
            if lang not in LANGUAGES:
                raise ValueError("❌ اللغة غير مدعومة.")
            app.config[f"user_lang_{chat_id}"] = lang
            send_message(chat_id, f"✅ تم تعيين اللغة إلى: {LANGUAGES[lang]}.")
        except ValueError as e:
            send_message(chat_id, str(e))
        return jsonify({"status": "ok"}), 200

    elif text:
        lang = app.config.get(f"user_lang_{chat_id}", DEFAULT_LANGUAGE)
        try:
            temp_audio = synthesize_speech(text, lang)
            send_audio(chat_id, temp_audio)
        except Exception as e:
            send_message(chat_id, f"❌ حدث خطأ أثناء تحويل النص إلى صوت: {e}")
        return jsonify({"status": "ok"}), 200

    send_message(chat_id, "❌ الرجاء إرسال نص صحيح.")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print(f"✅ تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)

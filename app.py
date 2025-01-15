import os
import requests
import pyttsx3
from flask import Flask, request, jsonify
from tempfile import NamedTemporaryFile

os.system('pip install pyttsx3')

# إعداد القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # توكن البوت
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي

if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

# إعداد اللغات والأصوات وسرعة الصوت
LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "fr": "Français",
    "es": "Español",
}

VOICES = {
    "male": "رجل",
    "female": "امرأة",
}

DEFAULT_LANGUAGE = "ar"
DEFAULT_VOICE = "male"
DEFAULT_SPEED = 150  # السرعة الافتراضية

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

def synthesize_speech(text, lang=DEFAULT_LANGUAGE, voice=DEFAULT_VOICE, speed=DEFAULT_SPEED):
    """تحويل النص إلى صوت باستخدام pyttsx3."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # اختيار الصوت
    for v in voices:
        if (voice == "male" and "male" in v.name.lower()) or (voice == "female" and "female" in v.name.lower()):
            engine.setProperty("voice", v.id)
            break

    # تعيين سرعة الصوت
    engine.setProperty("rate", speed)

    with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        engine.save_to_file(text, temp_audio.name)
        engine.runAndWait()
        return temp_audio

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
            "\n\n🎙️ *الأصوات المدعومة:*\n" +
            "\n".join([f"- `{key}`: {value}" for key, value in VOICES.items()]) +
            "\n\n⚙️ *أوامر التحكم:*\n"
            "`/lang [رمز اللغة]` - لتغيير اللغة.\n"
            "`/voice [male/female]` - لتغيير الصوت.\n"
            "`/speed [عدد]` - لتغيير سرعة الصوت (مثل 100-200).\n"
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

    elif text.startswith("/voice"):
        try:
            _, voice = text.split(maxsplit=1)
            if voice not in VOICES:
                raise ValueError("❌ الصوت غير مدعوم.")
            app.config[f"user_voice_{chat_id}"] = voice
            send_message(chat_id, f"✅ تم تعيين الصوت إلى: {VOICES[voice]}.")
        except ValueError as e:
            send_message(chat_id, str(e))
        return jsonify({"status": "ok"}), 200

    elif text.startswith("/speed"):
        try:
            _, speed = text.split(maxsplit=1)
            speed = int(speed)
            if speed < 50 or speed > 300:
                raise ValueError("❌ السرعة يجب أن تكون بين 50 و 300.")
            app.config[f"user_speed_{chat_id}"] = speed
            send_message(chat_id, f"✅ تم تعيين سرعة الصوت إلى: {speed}.")
        except ValueError as e:
            send_message(chat_id, str(e))
        return jsonify({"status": "ok"}), 200

    elif text:
        lang = app.config.get(f"user_lang_{chat_id}", DEFAULT_LANGUAGE)
        voice = app.config.get(f"user_voice_{chat_id}", DEFAULT_VOICE)
        speed = app.config.get(f"user_speed_{chat_id}", DEFAULT_SPEED)
        try:
            temp_audio = synthesize_speech(text, lang, voice, speed)
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

import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread

# تعيين القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # يجب وضع توكن البوت في متغير البيئة
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك العام (HTTPS مطلوب)
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي 5000

# التأكد من وجود API_TOKEN و WEBHOOK_URL
if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

def set_webhook():
    """إعداد Webhook للبوت على Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ تم إعداد Webhook بنجاح: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل في إعداد Webhook: {e}")

def send_message(chat_id, text):
    """إرسال رسالة إلى مستخدم Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل في إرسال الرسالة: {e}")

# محاكاة التفاعل مع الفيديو القصير
def interact_with_short_video(platform, video_url, actions_count):
    """محاكاة التفاعل مع مقاطع الفيديو القصيرة مثل ريلز أو تيك توك."""
    if platform == "tiktok":
        # محاكاة التفاعل مع TikTok
        for i in range(actions_count):
            try:
                print(f"✅ محاكاة التفاعل مع الفيديو على TikTok ({i + 1}/{actions_count})")
                # إضافة منطق التفاعل مع TikTok مثل الإعجاب أو التعليق
                time.sleep(2)  # الانتظار بين التفاعلات
            except Exception as e:
                print(f"❌ خطأ أثناء التفاعل مع الفيديو: {e}")
    elif platform == "instagram_reels":
        # محاكاة التفاعل مع Instagram Reels
        for i in range(actions_count):
            try:
                print(f"✅ محاكاة التفاعل مع الفيديو على Instagram Reels ({i + 1}/{actions_count})")
                # إضافة منطق التفاعل مع Reels مثل الإعجاب أو التعليق
                time.sleep(2)  # الانتظار بين التفاعلات
            except Exception as e:
                print(f"❌ خطأ أثناء التفاعل مع الفيديو: {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """معالجة الرسائل الواردة من Telegram."""
    data = request.get_json()
    if not data or "message" not in data:
        return "No message data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "مرحبًا! أرسل رابط الفيديو القصير وعدد التفاعلات المطلوبة بصيغة:\n`رابط_الفيديو عدد_التفاعلات`\nمثال:\n`https://www.tiktok.com/@user/video/12345 100`")
    elif "tiktok.com" in text or "instagram.com" in text:
        try:
            # استخدام regex للتحقق من صحة الرابط
            parts = text.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError("صيغة غير صحيحة! تأكد من إرسال الرابط مع عدد التفاعلات.")

            video_url, actions_count = parts
            if not re.match(r"(https?://)?(www\.)?(tiktok\.com|instagram\.com)/", video_url):
                raise ValueError("الرابط غير صالح! تأكد من استخدام رابط صحيح.")

            actions_count = int(actions_count)
            if actions_count <= 0:
                raise ValueError("عدد التفاعلات يجب أن يكون رقمًا صحيحًا أكبر من 0.")

            send_message(chat_id, f"✅ تم بدء التفاعل مع الفيديو:\n{video_url}\n📈 العدد المطلوب: {actions_count}")

            # تشغيل عملية التفاعل في Thread لتجنب تعليق الخادم
            Thread(target=interact_with_short_video, args=("tiktok", video_url, actions_count)).start()
        except ValueError as ve:
            send_message(chat_id, f"❌ خطأ في الصيغة: {ve}")
        except Exception as e:
            send_message(chat_id, f"❌ حدث خطأ: {e}")
    else:
        send_message(chat_id, "❌ صيغة غير صحيحة! أرسل رابط الفيديو وعدد التفاعلات المطلوبة.")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ بدء تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()  # إعداد Webhook عند بدء التشغيل
    app.run(host="0.0.0.0", port=PORT)

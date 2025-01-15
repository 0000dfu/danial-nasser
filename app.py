import os
import re
import time
import uuid
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

# قائمة لتسجيل الحسابات
accounts = {}

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

def interact_with_video(account_id, platform, video_url, actions_count):
    """محاكاة التفاعل مع مقاطع الفيديو القصيرة."""
    try:
        for i in range(actions_count):
            watch_time = 10 + (i % 5)  # مدة مشاهدة متغيرة لمحاكاة الوقت الحقيقي
            print(f"✅ الحساب {account_id}: مشاهدة الفيديو {video_url} ({i + 1}/{actions_count}) لمدة {watch_time} ثانية.")
            time.sleep(watch_time)
        print(f"✅ الحساب {account_id}: تم الانتهاء من التفاعل.")
    except Exception as e:
        print(f"❌ الحساب {account_id}: خطأ أثناء التفاعل: {e}")

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

            # إنشاء حساب جديد
            account_id = str(uuid.uuid4())
            accounts[account_id] = {"video_url": video_url, "actions_count": actions_count}

            send_message(chat_id, f"✅ تم إنشاء حساب جديد للتفاعل:\n📄 معرّف الحساب: `{account_id}`\n🎥 الفيديو: {video_url}\n📈 العدد المطلوب: {actions_count}")

            # تشغيل عملية التفاعل في Thread لتجنب تعليق الخادم
            Thread(target=interact_with_video, args=(account_id, "tiktok", video_url, actions_count)).start()
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

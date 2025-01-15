import os
import time
import requests
from flask import Flask, request
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# تعيين القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # يجب وضع توكن البوت في متغير البيئة
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك العام (HTTPS مطلوب)
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي 5000

if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

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

def interact_with_video_selenium(video_url, actions_count):
    """محاكاة التفاعل باستخدام Selenium."""
    try:
        # إعداد Selenium مع Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # تحديد مسار ChromeDriver
        chrome_service = Service("/usr/bin/chromedriver")

        # تشغيل المتصفح
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        print(f"✅ تم فتح المتصفح للتفاعل مع {video_url}")

        driver.get(video_url)
        time.sleep(5)  # انتظار تحميل الصفحة

        for i in range(actions_count):
            print(f"✅ مشاهدة الفيديو ({i + 1}/{actions_count}) لمدة 10 ثوانٍ.")
            time.sleep(10)  # محاكاة المشاهدة

        driver.quit()
        print("✅ تم الانتهاء من التفاعل.")
    except Exception as e:
        print(f"❌ خطأ أثناء التفاعل: {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """معالجة الرسائل الواردة من Telegram."""
    data = request.get_json()
    if not data or "message" not in data:
        return "No message data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "مرحبًا! أرسل رابط الفيديو القصير وعدد التفاعلات المطلوبة.")
    elif "instagram.com" in text or "tiktok.com" in text:
        try:
            video_url, actions_count = text.split(maxsplit=1)
            actions_count = int(actions_count)
            account_id = len(accounts) + 1
            accounts[account_id] = {"video_url": video_url, "actions_count": actions_count}

            send_message(chat_id, f"✅ تم إنشاء حساب جديد للتفاعل:\n📄 معرّف الحساب: {account_id}\n🎥 الفيديو: {video_url}\n📈 العدد المطلوب: {actions_count}")
            Thread(target=interact_with_video_selenium, args=(video_url, actions_count)).start()
        except Exception as e:
            send_message(chat_id, f"❌ خطأ: {e}")
    else:
        send_message(chat_id, "❌ صيغة غير صحيحة!")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ بدء تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)

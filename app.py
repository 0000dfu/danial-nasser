import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread
from random import uniform, choice, randint
import http.cookiejar as cookiejar

# قائمة الـ User-Agent لمحاكاة التصفح
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5043.102 Mobile Safari/537.36",
]

# استرداد المتغيرات البيئية
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 5000))

# تحقق من صحة الإعدادات
if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("API_TOKEN and WEBHOOK_URL must be set as environment variables.")

# إنشاء تطبيق Flask
app = Flask(__name__)

def set_webhook():
    """إعداد ويب هوك الخاص بتليجرام."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Webhook successfully set: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error setting webhook: {e}")

def send_message(chat_id, text):
    """إرسال رسالة للمستخدم عبر تليجرام."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending message: {e}")

def create_fake_cookies():
    """إنشاء بيانات كوكيز وهمية لمحاكاة السلوك الطبيعي."""
    cookies = cookiejar.LWPCookieJar()
    cookies.set_cookie(cookiejar.Cookie(
        version=0,
        name="CONSENT",
        value="YES+cb.20220310-17-p0.en+FX+678",
        port=None,
        port_specified=False,
        domain=".youtube.com",
        domain_specified=True,
        domain_initial_dot=True,
        path="/",
        path_specified=True,
        secure=True,
        expires=int(time.time()) + 3600,
        discard=False,
        comment=None,
        comment_url=None,
        rest={"HttpOnly": None},
        rfc2109=False
    ))
    cookies.set_cookie(cookiejar.Cookie(
        version=0,
        name="VISITOR_INFO1_LIVE",
        value="random_value_" + str(randint(100000, 999999)),
        port=None,
        port_specified=False,
        domain=".youtube.com",
        domain_specified=True,
        domain_initial_dot=True,
        path="/",
        path_specified=True,
        secure=True,
        expires=int(time.time()) + 3600,
        discard=False,
        comment=None,
        comment_url=None,
        rest={"HttpOnly": None},
        rfc2109=False
    ))
    return cookies

def simulate_interaction(video_url, headers, cookies):
    """محاكاة طلب إلى YouTube باستخدام الكوكيز."""
    try:
        response = requests.get(video_url, headers=headers, cookies=cookies, timeout=10)
        if response.status_code == 200:
            print(f"✅ Interaction started for: {video_url}")
            time.sleep(uniform(10, 60))  # تأخير عشوائي لمحاكاة مشاهدة طبيعية
            print(f"✅ Interaction completed for: {video_url}")
            return True
        else:
            print(f"❌ Failed interaction. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during interaction: {e}")
        return False

def increase_views(video_url, views_count, chat_id):
    """محاكاة زيادة المشاهدات باستخدام كوكيز وهمية."""
    for i in range(views_count):
        view_id = i + 1
        headers = {"User-Agent": choice(USER_AGENTS)}
        cookies = create_fake_cookies()
        success = simulate_interaction(video_url, headers, cookies)
        if success:
            send_message(chat_id, f"✅ View {view_id}/{views_count} simulated successfully! 🎥")
        else:
            send_message(chat_id, f"❌ Failed to simulate view {view_id}.")
        time.sleep(uniform(5, 15))  # تأخير عشوائي بين الطلبات

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """معالجة طلبات تليجرام."""
    data = request.get_json()
    if not data or "message" not in data:
        return "Invalid data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        welcome_message = (
            "👋 *Welcome!*\n\n"
            "To simulate views on a video, send the video URL and desired view count in the format:\n"
            "<video_url> <view_count>\n\n"
            "📌 Example:\nhttps://www.youtube.com/watch?v=example 100"
        )
        send_message(chat_id, welcome_message)
    elif re.match(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+", text):
        try:
            video_url, views_count = text.rsplit(maxsplit=1)
            views_count = int(views_count)
            if views_count <= 0:
                raise ValueError("Views count must be positive.")
            send_message(chat_id, f"✅ Starting simulation for {views_count} views.")
            Thread(target=increase_views, args=(video_url, views_count, chat_id)).start()
        except ValueError as ve:
            send_message(chat_id, f"❌ Invalid input: {ve}")
        except Exception as e:
            send_message(chat_id, f"❌ An unexpected error occurred: {e}")
    else:
        send_message(chat_id, "❌ Invalid URL or format. Please send the video URL and view count.")

    return "OK", 200

if __name__ == "__main__":
    print(f"Starting app on port {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)

# path: /enhanced_youtube_view_simulator.py

import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread
from random import uniform, choice, randint
import http.cookiejar as cookiejar
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5043.102 Mobile Safari/537.36",
]
PROXY_LIST = os.getenv("PROXY_LIST", "").split(",")  # Optional proxies from environment

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 5000))

# Flask application instance
app = Flask(__name__)

def load_proxies():
    """Load proxies from environment variable."""
    return [{"http": proxy, "https": proxy} for proxy in PROXY_LIST if proxy]

PROXIES = load_proxies()

def set_webhook():
    """Setup Telegram webhook."""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/setWebhook",
            json={"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
        )
        response.raise_for_status()
        print(f"✅ Webhook set successfully: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.RequestException as e:
        print(f"❌ Error setting webhook: {e}")

def send_message(chat_id, text):
    """Send message to a user via Telegram bot."""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{API_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error sending message: {e}")

def create_fake_cookies():
    """Generate realistic cookies for YouTube interaction."""
    cookies = cookiejar.LWPCookieJar()
    cookies.set_cookie(cookiejar.Cookie(
        version=0,
        name="CONSENT",
        value="YES+cb.20230417-18-p0.en+FX+103",
        domain=".youtube.com",
        path="/",
        secure=True,
        expires=int(time.time()) + 3600,
        rest={"HttpOnly": None},
        rfc2109=False
    ))
    cookies.set_cookie(cookiejar.Cookie(
        version=0,
        name="VISITOR_INFO1_LIVE",
        value="random_value_" + str(randint(100000, 999999)),
        domain=".youtube.com",
        path="/",
        secure=True,
        expires=int(time.time()) + 3600,
        rest={"HttpOnly": None},
        rfc2109=False
    ))
    return cookies

def simulate_interaction(video_url, headers, cookies, proxy=None):
    """Simulate a realistic interaction with YouTube."""
    try:
        response = requests.get(
            video_url, headers=headers, cookies=cookies, proxies=proxy, timeout=15
        )
        if response.status_code == 200:
            print(f"✅ View started for {video_url}")
            time.sleep(uniform(15, 60))  # Simulated watch duration
            print(f"✅ View completed for {video_url}")
            return True
        else:
            print(f"❌ Failed view: HTTP {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error during interaction: {e}")
        return False

def increase_views(video_url, views_count, chat_id):
    """Simulate multiple views."""
    for view_id in range(1, views_count + 1):
        headers = {"User-Agent": choice(USER_AGENTS)}
        cookies = create_fake_cookies()
        proxy = choice(PROXIES) if PROXIES else None
        success = simulate_interaction(video_url, headers, cookies, proxy)
        if success:
            send_message(chat_id, f"✅ View {view_id}/{views_count} simulated successfully!")
        else:
            send_message(chat_id, f"❌ Failed to simulate view {view_id}")
        time.sleep(uniform(10, 30))  # Delay between views for realism

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """Handle Telegram bot requests."""
    data = request.get_json()
    if not data or "message" not in data:
        return "Invalid data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        welcome_message = (
            "👋 Welcome to the YouTube view simulator bot!\n"
            "Send a YouTube video URL followed by the number of views to simulate.\n\n"
            "📌 Example:\nhttps://youtube.com/watch?v=example 100"
        )
        send_message(chat_id, welcome_message)
    elif re.match(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+", text):
        try:
            video_url, views_count = text.rsplit(maxsplit=1)
            views_count = int(views_count)
            if views_count <= 0:
                raise ValueError("Views count must be positive.")
            send_message(chat_id, f"Starting {views_count} view simulations for {video_url}")
            Thread(target=increase_views, args=(video_url, views_count, chat_id)).start()
        except ValueError as ve:
            send_message(chat_id, f"❌ Invalid input: {ve}")
        except Exception as e:
            send_message(chat_id, f"❌ Unexpected error: {e}")
    else:
        send_message(chat_id, "❌ Invalid format. Please use `<video_url> <view_count>`.")
    return "OK", 200

if __name__ == "__main__":
    print(f"Starting Flask server on port {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)

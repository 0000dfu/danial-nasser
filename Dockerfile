# استخدام صورة Python
FROM python:3.9-slim

# تثبيت Chrome و ChromeDriver
RUN apt-get update && apt-get install -y wget gnupg unzip && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    apt-get clean

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install -r requirements.txt

# نسخ الملفات وتشغيل التطبيق
COPY . .
CMD ["python", "app.py"]

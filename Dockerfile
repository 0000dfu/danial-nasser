# استخدم صورة Python الأساسية
FROM python:3.10-slim

# تثبيت الحزم الأساسية
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    && apt-get clean

# إضافة مفتاح Google Chrome الرسمي
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# تثبيت Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# تنزيل وتثبيت Chromedriver
RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# تعيين PATH الافتراضي لـ Chrome وChromedriver
ENV PATH="/usr/bin/google-chrome:/usr/bin/chromedriver:$PATH"

# نسخ ملفات المشروع
WORKDIR /app
COPY . /app

# تثبيت متطلبات المشروع
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["python", "app.py"]

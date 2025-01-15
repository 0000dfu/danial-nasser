FROM python:3.9-slim

# تثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    chromium chromium-driver

# نسخ الملفات
WORKDIR /app
COPY . /app

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["python", "app.py"]

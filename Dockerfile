# استخدام صورة Python الرسمية
FROM python:3.10-slim

# تثبيت الحزم الأساسية وChrome وChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    && apt-get clean

# نسخ المتطلبات وتثبيت مكتبات Python المطلوبة
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . /app

# تحديد الأمر الافتراضي لتشغيل التطبيق
CMD ["python", "app.py"]

# استخدام صورة Python خفيفة
FROM python:3.9-slim

# تثبيت المتطلبات
RUN apt-get update && apt-get install -y \
    libasound2 libpulse0 \
    && apt-get clean

# نسخ الملفات
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

# تشغيل التطبيق
CMD ["python", "app.py"]

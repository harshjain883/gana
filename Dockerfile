FROM python:3.10-slim

WORKDIR /app

# System dependencies इनस्टॉल करें
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python requirements कॉपी और इनस्टॉल करें
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# प्रोजेक्ट की बाकी फाइल्स कॉपी करें
COPY . .

# Start script को executable बनाएं
RUN chmod +x start.sh

# Railway का डिफ़ॉल्ट पोर्ट
EXPOSE 8000

# स्टार्टअप स्क्रिप्ट से ऐप रन करें
CMD ["./start.sh"]

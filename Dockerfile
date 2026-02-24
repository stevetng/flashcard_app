FROM python:3.12-slim

# Install LibreOffice for .ppt to .pptx conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends libreoffice-impress && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn web_app:app --bind 0.0.0.0:${PORT:-8000}

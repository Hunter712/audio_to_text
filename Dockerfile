FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg flac && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "audio_to_text.py"]

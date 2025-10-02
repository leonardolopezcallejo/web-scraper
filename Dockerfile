# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY app /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "8001"]

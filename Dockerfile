FROM python:3.11-slim

WORKDIR /app

# Caché de dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia código fuente
COPY . /app

# Puerto expuesto
EXPOSE 8000

# Entry point correcto
CMD ["uvicorn", "frontend_server:app", "--host", "0.0.0.0", "--port", "8000"]

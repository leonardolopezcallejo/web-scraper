# Etapa base con Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /code

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el backend y frontend
COPY app ./app
COPY frontend ./frontend

# Exponer el puerto estándar
EXPOSE 8000

# Comando para ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "app.scraper_api:app", "--host", "0.0.0.0", "--port", "8000"]

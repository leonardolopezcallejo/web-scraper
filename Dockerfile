# Etapa base
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo requirements.txt primero (para cachear dependencias)
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del backend
COPY ./app /app

# Expone el puerto de FastAPI
EXPOSE 8000

# Comando para ejecutar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

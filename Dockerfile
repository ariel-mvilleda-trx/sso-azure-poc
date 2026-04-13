# Dockerfile para la API FastAPI

FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY api.py .

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "api.py"]

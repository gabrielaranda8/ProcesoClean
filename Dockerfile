# Usa una imagen base con Python
FROM python:3.10-slim

# Instala las dependencias necesarias para Playwright
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    xvfb \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && apt-get clean

# Configura el directorio de trabajo
WORKDIR /app

# Crea el directorio de descargas y asigna los permisos
RUN mkdir -p /downloads && chmod -R 777 /downloads

# Copia los archivos de la aplicación
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install

# Comando por defecto
CMD ["python", "-u", "app.py"]

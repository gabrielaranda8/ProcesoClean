# Usa una imagen base con Python
FROM python:3.10-slim

# Instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    xvfb \
    && apt-get clean

# Instala Google Chrome
RUN curl -sS -L https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb

# Instala ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    curl -sS -L https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -o chromedriver.zip && \
    unzip chromedriver.zip -d /usr/local/bin/ && \
    rm chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Configura el directorio de trabajo
WORKDIR /app

# Crea el directorio de descargas y asigna los permisos
RUN mkdir -p /downloads && chmod -R 777 /downloads

# Copia los archivos de la aplicación
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto
CMD ["python", "app.py"]

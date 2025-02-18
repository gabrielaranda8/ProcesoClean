# Usa una imagen base con Python
FROM python:3.10-slim

# Instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    xvfb \
    && apt-get clean

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

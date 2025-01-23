#!/bin/bash

# Actualiza los paquetes e instala Chromium y sus dependencias
apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    xdg-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
pip install -r requirements.txt
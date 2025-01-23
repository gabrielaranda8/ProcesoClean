#!/bin/bash

# Actualizar paquetes e instalar Chromium y dependencias
apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    xdg-utils

# Limpiar el sistema para reducir el tamaño
apt-get clean && rm -rf /var/lib/apt/lists/*

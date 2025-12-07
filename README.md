# SCARF-ITE: Sistema de Control de Acceso por Reconocimiento Facial

SCARF-ITE es un prototipo de control de acceso basado en reconocimiento facial, diseñado para verificar la identidad del personal autorizado mediante visión por computadora. El sistema registra todos los intentos de ingreso (tanto exitosos como fallidos) para garantizar la auditoría y trazabilidad de los accesos.

## Descripción

El sistema utiliza una cámara de videovigilancia inalámbrica de alta resolución (3 megapíxeles) con conectividad WiFi, para capturar imágenes faciales en tiempo real. Además, se integra un **Raspberry Pi 5 de 8GB**, que se encarga de recibir los sockets del lado del cliente y enviar señales al microcontrolador el cual ejecuta comandos, simulando el sistema de control de acceso. El objetivo principal es garantizar que solo el personal autorizado pueda ingresar a áreas restringidas, proporcionando un control eficiente y seguro.

## Características

- **Reconocimiento facial en tiempo real**.
- **Registro de intentos de acceso** (tanto exitosos como fallidos).
- **Cámara de videovigilancia inalámbrica de alta resolución (3 MP)**.
- **Raspberry Pi 5 de 8GB** para gestionar los datos de acceso.
- **Conectividad WiFi**.

## Requisitos

### Hardware

- Raspberry Pi 5 (8GB)
- Cámara inalámbrica de 3 MP con conectividad WiFi
- Microcontrolador Arduino Uno
- Servomotor
- Buzzer
- Protoboard

### Software

- Sistema operativo Raspberry Pi (Raspberry Pi OS Lite)
- CMake 4.2.0 (para permitir instalacion de librerias como dlib)
- OpenMediaVault (software NAS para el Raspberry Pi)

## Instalacion
### 1️⃣ Clonar el repositorio (tanto local como en Raspberry Pi)
- Local:
git clone https://github.com/slimh4cker/SCARF-ITE.git
cd SCARF-ITE

- Raspberry Pi:
cd /opt
git clone https://github.com/slimh4cker/SCARF-ITE.git
cd SCARF-ITE

### 2️⃣ Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   (Windows: .venv\Scripts\activate)
pyenv activate venv         (Raspberry Pi)

### 3️⃣ Instalar dependencias
cd src/backend/librerias
pip install -r requirements.txt

### 4️⃣ Configurar variables de entorno
SCARF-ITE/src/.env

### 5️⃣ Iniciar el servidor socket (en Raspberry Pi)
cd SCARF-ITE
python3 src/backend/server_socket.py

### 6️⃣ Iniciar el programa
python src/main_gui.py

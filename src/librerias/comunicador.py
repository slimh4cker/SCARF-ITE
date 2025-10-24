import sys
import time
import serial

#!/usr/bin/env python3
# librerias/comunicador.py
# Envia una cadena de texto al Arduino desde una Raspberry Pi usando pyserial

import serial.tools.list_ports


def encontrar_puerto_arduino():
    """Busca un puerto serie que parezca un Arduino (ACM, USB o con 'Arduino' en la descripción)."""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        device = (p.device or "").lower()
        if "arduino" in desc or "arduino" in device or "acm" in device or "usb" in device:
            return p.device
    # Si no se detecta, devuelve None
    return None

def enviar_comando_arduino(puerto, comando, baud_rate=9600):
    """
    Envía un comando por el puerto serial al Arduino.
    
    Parámetros:
      puerto (str): nombre del puerto (por ejemplo '/dev/ttyUSB0' o 'COM3')
      comando (str): texto del comando a enviar (por ejemplo 'abrir_puerta')
      baud_rate (int): velocidad del puerto serial (por defecto 9600)
    """
    try:
        # Conectar con el Arduino
        arduino = serial.Serial(puerto, baud_rate, timeout=1)
        time.sleep(2)  # Esperar a que el Arduino se reinicie

        # Enviar comando seguido de salto de línea
        arduino.write((comando + '\n').encode('utf-8'))
        print(f"✅ Comando enviado: {comando}")

    except serial.SerialException:
        print("❌ Error: No se pudo abrir el puerto serial. Verifica la conexión y permisos.")
    finally:
        # Cerrar el puerto siempre
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()
            print("🔌 Conexión cerrada.")


if __name__ == "__main__":
    # Uso: python3 comunicador.py "Mensaje a enviar"
    texto = "abrir_puerta"

    try:
        puerto = '/dev/ttyUSB0'  # o poner '/dev/ttyACM0' explícito si se conoce
        respuesta = enviar_comando_arduino(puerto, texto, baud_rate=9600)
        print('Se ha enviado el comando al Arduino.')
        
    except Exception as e:
        print("Error:", e)
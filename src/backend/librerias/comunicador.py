import sys
import time
import serial
import asyncio
from backend.client_socket import enviar_comando_laptop

#!/usr/bin/env python3
# librerias/comunicador.py
# En este archivo se definen funciones para comunicarse con un Arduino a través de un puerto serial.

import serial.tools.list_ports


def encontrar_puerto_arduino():
    """
    Busca un puerto serie que parezca un Arduino (ACM, USB o con 'Arduino' en la descripción).
    No recibe parámetros.
    Devuelve el nombre del puerto (str) o None si no se encuentra ninguno.
    """
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = (p.description or "").lower()
        device = (p.device or "").lower()
        if "arduino" in desc or "arduino" in device or "acm" in device or "usb" in device:
            return p.device
    # Si no se detecta, devuelve None
    return None

async def enviar_comando_arduino(comando):
    """
    Envía un comando por el puerto serial al Arduino (versión asíncrona).
    Si ya hay otro comando en proceso, no envía uno nuevo.
    Devuelve True si se envió el comando, False si fue ignorado o falló.
    """

    enviar_comando_laptop(comando)

    """ # lock global y creación perezosa (dentro del event loop)
    global _arduino_send_lock
    if "_arduino_send_lock" not in globals() or _arduino_send_lock is None:
        _arduino_send_lock = asyncio.Lock()

    # Si ya está en uso, no enviamos otro comando
    if _arduino_send_lock.locked():
        return False
    

    await _arduino_send_lock.acquire()
    try:
        # Abrir el puerto en un thread para no bloquear el event loop
        arduino = await asyncio.to_thread(serial.Serial, puerto, baud_rate, timeout=1)
        # Esperar asincrónicamente a que el Arduino se reinicie
        await asyncio.sleep(2)
        # Enviar comando en un thread (operación de E/S)
        await asyncio.to_thread(arduino.write, (comando + '\n').encode('utf-8'))
        print(f" Comando enviado: {comando}")

    except Exception as e:
        print(" Error: No se pudo abrir el puerto serial. Verifica la conexión y permisos.", e)
    finally:
        # Asegurar cierre y liberación del lock
        try:
            if 'arduino' in locals() and getattr(arduino, 'is_open', False):
                await asyncio.to_thread(arduino.close)
                print("🔌 Conexión cerrada.")
        finally:
            _arduino_send_lock.release()
 """

if __name__ == "__main__":
    # Uso: python3 comunicador.py "Mensaje a enviar"
    abrir = "abrir_puerta"
    denegar = "acceso_denegado"
    print("Buscando puerto del Arduino...")
    print(encontrar_puerto_arduino())

    try:
        puerto = '/dev/ttyUSB0'  # o '/dev/ttyACM0' si corresponde
        print("Puerto utilizado:", puerto)

        async def main():
            print(f"Enviando comando {denegar} al Arduino...")
            await enviar_comando_arduino(puerto, denegar, baud_rate=9600)
            await asyncio.sleep(3)
            print(f"Enviando comando {abrir} al Arduino...")
            await enviar_comando_arduino(puerto, abrir, baud_rate=9600)

        asyncio.run(main())

    except Exception as e:
        print("Error:", e)
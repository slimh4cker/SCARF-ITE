import socket
import asyncio
import serial
import serial.tools.list_ports

# Función para encontrar el puerto del Arduino
def encontrar_puerto_arduino():
    ports = list(serial.tools.list_ports.comports())    
    for p in ports:
        desc = (p.description or "").lower()
        device = (p.device or "").lower()
        if "arduino" in desc or "arduino" in device or "acm" in device or "usb" in device:
            return p.device
    return None

# Función para enviar un comando al Arduino
async def enviar_comando_arduino(puerto, comando, baud_rate=9600):
    global _arduino_send_lock
    if "_arduino_send_lock" not in globals() or _arduino_send_lock is None:
        _arduino_send_lock = asyncio.Lock()

    if _arduino_send_lock.locked():
        return False

    await _arduino_send_lock.acquire()
    try:
        arduino = await asyncio.to_thread(serial.Serial, puerto, baud_rate, timeout=1)
        await asyncio.sleep(2)
        await asyncio.to_thread(arduino.write, (comando + '\n').encode('utf-8'))
        print(f"Comando enviado: {comando}")
    except Exception as e:
        print("Error al enviar el comando:", e)
    finally:
        try:
            if 'arduino' in locals() and getattr(arduino, 'is_open', False):
                await asyncio.to_thread(arduino.close)
                print("🔌 Conexión cerrada.")
        finally:
            _arduino_send_lock.release()

# Función para manejar la conexión del cliente (laptop)
def manejar_conexion(cliente_socket, puerto_arduino):
    try:
        # Recibir comando desde la laptop
        comando = cliente_socket.recv(1024).decode('utf-8')
        if comando:
            print(f"Comando recibido: {comando}")
            # Enviar comando al Arduino
            if comando == "abrir_puerta":
                asyncio.run(enviar_comando_arduino(puerto_arduino, "abrir_puerta"))
            elif comando == "acceso_denegado":
                asyncio.run(enviar_comando_arduino(puerto_arduino, "acceso_denegado"))
            else:
                print(f"Comando desconocido: {comando}")
        cliente_socket.close()
    except Exception as e:
        print(f"Error al manejar la conexión: {e}")

# Función principal para escuchar el puerto del servidor
def servidor_socket():
    puerto_servidor = 5000  # Puerto donde escucha el servidor
    puerto_arduino = encontrar_puerto_arduino()  # Encontrar el puerto del Arduino

    if not puerto_arduino:
        print("No se encontró un Arduino conectado.")
        return

    print(f"Puerto del Arduino: {puerto_arduino}")

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.bind(('0.0.0.0', puerto_servidor))  # Escuchar en todas las interfaces
    servidor_socket.listen(1)

    print(f"Servidor escuchando en puerto {puerto_servidor}...")

    while True:
        cliente_socket, _ = servidor_socket.accept()
        print("Cliente conectado.")
        manejar_conexion(cliente_socket, puerto_arduino)

if __name__ == "__main__":
    servidor_socket()

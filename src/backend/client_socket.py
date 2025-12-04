'''
Este archivo representa el cliente socket
el cual enviara comandos desde cualquier laptop
con el programa, hacia el servidor socket (Rasp Pi)
de ese modo envia el comando para ejecutar el arduino


'''

import socket
import os
from dotenv import load_dotenv


def enviar_comando_laptop(comando):
    load_dotenv()
    ip_raspberry_pi = os.getenv('IP_RASPBERRY')
    puerto = int(os.getenv('PUERTO_RASPBERRY'))

    try:
        # Crear socket
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((ip_raspberry_pi, puerto))
        cliente_socket.send(comando.encode('utf-8'))
        cliente_socket.close()
        print(f"Comando {comando} enviado a la Raspberry Pi.")
    except Exception as e:
        print("Error al enviar comando:", e)

# ejemplo de uso (ponerlo en la GUI Main o donde es necesario)
def al_detectar_rostro():
    # Si el rostro es reconocido, enviar el comando para abrir la puerta
    enviar_comando_laptop("abrir_puerta")

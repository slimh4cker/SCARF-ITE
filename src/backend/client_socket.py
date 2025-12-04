'''
Este archivo representa el cliente socket
el cual enviara comandos desde cualquier laptop
con el programa, hacia el servidor socket (Rasp Pi)
de ese modo envia el comando para ejecutar el arduino


'''

import socket

def enviar_comando_laptop(comando):
    # Dirección IP de la Raspberry Pi
    ip_raspberry_pi = '10.4.10.9'  # IP de tu Raspberry Pi
    puerto = 5000  # Puerto donde escucha el servidor en Raspberry Pi

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

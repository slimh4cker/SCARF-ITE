 # Configuración de la base de datos
# config.py
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ncontradeMariaDB25!",     # tu contraseña si tiene
        database="reconocimiento",
        charset="utf8mb4",  # Solo utf8mb4, sin _0900_ai_ci
        collation="utf8mb4_general_ci"

    )

#Ruta donde se alojan las fotos en la Raspberry Pi
RUTA_FOTOS = "/srv/dev-disk-by-uuid-d0b97ed4-2c72-469f-926a-a8b480f908bc/scarf-ite"

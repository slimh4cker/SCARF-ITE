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

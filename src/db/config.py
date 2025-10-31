 # Configuración de la base de datos
# config.py
import mysql.connector
from dotenv import load_dotenv
import os



load_dotenv()

HOST = os.getenv('DB_HOST')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASS')
DATABASE = os.getenv('DB_NAME')
CHARSET = os.getenv('CHARSET')
COLLATION = os.getenv('COLLATION')



def conectar():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        charset=CHARSET,
        collation=COLLATION

)

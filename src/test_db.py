import mysql.connector
from mysql.connector import errorcode

# -----------------------------------------------------------------
# --- CONFIGURACIÓN: Edita estos 5 valores ---
# -----------------------------------------------------------------
# La IP pública o privada del servidor donde está la BD
HOST_IP = "127.0.0.1"  # O la IP pública si es por internet

# El puerto (3306 es el default de MySQL)
PUERTO = 3306

# El usuario que creaste para acceso remoto
USUARIO = "root"

# La contraseña que le asignaste a ese usuario
CONTRASENA = "1234"

# El nombre de la base de datos a la que quieres acceder
NOMBRE_BD = "reconocimiento"

# (Opcional) Una tabla que sepas que existe para probar la lectura
NOMBRE_TABLA_TEST = "usuarios"
# -----------------------------------------------------------------


def probar_conexion():
    """
    Intenta conectarse y leer datos de la base de datos.
    """
    try:
        print(f"Intentando conectar a {HOST_IP}:{PUERTO}...")
        
        # 1. Intento de conexión
        conexion = mysql.connector.connect(
            host=HOST_IP,
            port=PUERTO,
            user=USUARIO,
            password=CONTRASENA,
            database=NOMBRE_BD
        )
        
        if conexion.is_connected():
            print("\n¡ÉXITO! Conexión establecida correctamente.")
            
            cursor = conexion.cursor()
            
            # 2. Prueba de "ping" (versión del servidor)
            print("--- Obteniendo versión del servidor ---")
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Versión de MySQL: {version[0]}")
            
            # 3. Prueba de lectura de una tabla
            print(f"\n--- Intentando leer 1 registro de la tabla '{NOMBRE_TABLA_TEST}' ---")
            try:
                cursor.execute(f"SELECT * FROM {NOMBRE_TABLA_TEST} LIMIT 1")
                registro = cursor.fetchone()
                if registro:
                    print("¡Éxito! Se pudo leer un registro:")
                    print(registro)
                else:
                    print(f"Se pudo consultar la tabla, pero no se encontraron registros en '{NOMBRE_TABLA_TEST}'.")
            
            except mysql.connector.Error as err_tabla:
                print(f"\n¡FALLO EN LECTURA DE TABLA! No se pudo leer '{NOMBRE_TABLA_TEST}'.")
                print(f"Error: {err_tabla.msg}")
                print("Verifica que la tabla exista y que el usuario '{USUARIO}' tenga permisos de SELECT.")

    except mysql.connector.Error as err:
        # Aquí es donde verás los errores de conexión
        print(f"\n¡FALLO LA CONEXIÓN!")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Acceso denegado.")
            print(f"Revisa que el usuario '{USUARIO}' y la contraseña sean correctos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Error: La base de datos '{NOMBRE_BD}' no existe.")
        else:
            print(f"Error inesperado: {err.msg}")
            print("\nPosibles causas:")
            print(f"  1. ¿La IP {HOST_IP} es correcta?")
            print(f"  2. ¿El puerto {PUERTO} está abierto en el firewall del servidor?")
            print(f"  3. ¿El usuario '{USUARIO}' tiene permisos para conectarse desde tu IP actual?")

    finally:
        # Cierra la conexión si se estableció
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\nConexión cerrada.")

# --- Ejecutar el script ---
if __name__ == "__main__":
    probar_conexion()

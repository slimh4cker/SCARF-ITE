from backend.db.config import conectar
import time
import threading
from dotenv import load_dotenv
import os

load_dotenv()

class Logs:
    """
    Clase para gestionar el registro y consulta de logs de autenticación de usuarios.
    
    Proporciona métodos para registrar intentos de acceso (exitosos/fallidos) 
    y consultar estadísticas de logs desde la base de datos.
    
    Estados de los logs:
    - True o 1: Intento exitoso
    - False o 0: Intento fallido
    """
    
    def __init__(self):
        """
        Inicializa la clase Logs con contadores en memoria.
        
        Los contadores se pueden sincronizar con la base de datos mediante
        los métodos de consulta correspondientes.
        """
        # Contadores locales (opcional, se pueden llenar desde la BD)
        self.__intentos_totales = 0      # Número total de intentos registrados
        self.__intentos_exitosos = 0     # Número de intentos exitosos (status_log = True/1)
        self.__intentos_fallidos = 0     # Número de intentos fallidos (status_log = False/0)
        self.__id_usuario = ""           # ID del usuario actual (se establece automáticamente)
        self.__presicion = 0 # Presición del reconocimiento en porcentaje
        self.__taza_error = 0 # Error del reconocimiento en porcentaje
        self.__efectividad = "" # Valor cuantitavivo de la efectividad

        # Cooldown para no saturar la base de datos con logs repetidos
        self.log_cooldown_seconds = int(os.getenv("COOLDOWN_DETECTION"))  # No registrar al mismo usuario más de una vez cada 10 segundos
        self.last_log_time_by_user = {} # Diccionario para guardar {id_usuario: timestamp}
        self.log_lock = threading.Lock() # Para manejar concurrencia al acceder al diccionario

    # ==========================
    # MÉTODOS PRIVADOS INTERNOS
    # ==========================
    
    def __conexion(self):
        """
        Crea y retorna una conexión a la base de datos.
        
        Returns:
            object: Conexión a la base de datos
        """
        return conectar()

    def __obtener_id_usuario(self, nombre: str) -> int:
        """
        Obtiene el ID de usuario a partir del nombre.
        
        Args:
            nombre (str): Nombre del usuario a buscar
            
        Returns:
            int: ID del usuario si existe, None si no se encuentra
            
        Note:
            El nombre se convierte a minúsculas automáticamente
        """
        conn = conectar()
        cursor = conn.cursor()
        sql = "SELECT id FROM usuarios WHERE nombre = %s"
        cursor.execute(sql, (nombre,))
        result = cursor.fetchone()
        conn.close()
        print(result)
        self.__id_usuario = result[0] if result else None
        return self.__id_usuario

    def __cuantificar_efectividad(self):
        presicion = self.__presicion
        label_efectividad = ("Extremadamente positiva", "Muy Positiva", "Mayormente positiva",
                            "Variada", "Mayormente negativa", "Muy negativa", "Extremadamente negativa")
        
        if presicion <= 9:
            return label_efectividad[-1]
        elif presicion <= 19:
            return label_efectividad[-2]
        elif presicion <= 39:
            return label_efectividad[-3]
        elif presicion <= 69:
            return label_efectividad[-4]
        elif presicion <= 79:
            return label_efectividad[-5]
        elif presicion <= 94:
            return label_efectividad[-6]
        else:
            return label_efectividad[-7]



    # ==========================
    # MÉTODOS DE REGISTRO
    # ==========================

    def __registrar_log(self, id_usuario: int, status_log: bool) -> None:
        """
        Registra un intento de acceso en la tabla logs.
        
        Args:
            nombre (str): Nombre del usuario que realiza el intento
            status_log (bool): Estado del intento
                - True: Intento exitoso
                - False: Intento fallido
                
        Note:
            - Actualiza los contadores en memoria
            - Muestra un mensaje en consola con el resultado
            - Si el usuario no existe, no registra el log
        """
        conn = self.__conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO logs (id_usuario, status_log) VALUES (%s, %s)"
        cursor.execute(sql, (id_usuario, status_log))
        conn.commit()
        conn.close()

        # Actualiza contadores en memoria
        self.__intentos_totales += 1
        if status_log:
            self.__intentos_exitosos += 1
        else:
            self.__intentos_fallidos += 1
        
    
    def ejecutar(self, status_log: bool, id_usuario=None) -> None:
        """
        Ejecuta __registrar_log en un hilo separado para no bloquear la aplicación.
        Incluye un cooldown para evitar registros duplicados en un corto período de tiempo.
        """
        # Si es un intento fallido (intruso), el id_usuario es None.
        # Usamos una clave especial para los intrusos para aplicarles cooldown también.
        key = id_usuario if id_usuario is not None else "intruso"

        with self.log_lock:
            current_time = time.time()
            last_log_time = self.last_log_time_by_user.get(key, 0)

            # Comprobar si ha pasado suficiente tiempo desde el último log para esta clave
            if current_time - last_log_time < self.log_cooldown_seconds:
                # No ha pasado suficiente tiempo, no hacer nada.
                return
            
            # Ha pasado suficiente tiempo, actualizar el tiempo del último log.
            self.last_log_time_by_user[key] = current_time

        # Iniciar el registro en un hilo separado
        thread = threading.Thread(target=self.__registrar_log, args=(id_usuario, status_log), daemon=True)
        thread.start()

    # ==========================
    # MÉTODOS DE CONSULTA
    # ==========================
    
    def fetch_data(self) -> int:
        """
        Devuelve el total de intentos registrados en la base de datos.
        
        Returns:
            int: Número total de intentos registrados
            
        Note:
            Actualiza el contador en memoria (self.intentos_totales)
        """
        conn = self.__conexion()
        cursor = conn.cursor()
        # Obtención de datos totales
        cursor.execute("SELECT COUNT(*) FROM logs")
        result_logs = cursor.fetchone()
        self.__intentos_totales = result_logs[0] if result_logs else 0

        # Obtención de datos exitosos
        cursor.execute("SELECT COUNT(*) FROM logs WHERE status_log = TRUE")
        result_success = cursor.fetchone()
        self.__intentos_exitosos = result_success[0] if result_success else 0

        # Obtención de datos fallidos
        cursor.execute("SELECT COUNT(*) FROM logs WHERE status_log = FALSE")
        result_fail = cursor.fetchone()
        self.__intentos_fallidos = result_fail[0] if result_fail else 0

        # Fin de la sesión
        conn.close()
        self.__presicion = round((self.__intentos_exitosos / self.__intentos_totales) * 100, 2)
        self.__taza_error = round((self.__intentos_fallidos / self.__intentos_totales) * 100, 2)
        self.__efectividad = self.__cuantificar_efectividad()
    
    def obtener_intentos_totales(self) -> int:
        """
        Devuelve el total de intentos.
        
        Returns:
            int: Número de intentos con status_log
        return self.intentos_exitosos
        """
        return self.__intentos_totales

    def obtener_intentos_exitosos(self) -> int:
        """
        Devuelve el total de intentos exitosos.
        
        Returns:
            int: Número de intentos con status_log = True/1
            
        Note:
            Actualiza el contador en memoria (self.intentos_exitosos)
        """
        return self.__intentos_exitosos

    def obtener_intentos_fallidos(self) -> int:
        """
        Devuelve el total de intentos fallidos.
        
        Returns:
            int: Número de intentos con status_log = False/0
            
        Note:
            Actualiza el contador en memoria (self.intentos_fallidos)
        """
        return self.__intentos_fallidos

    def obtener_presicion(self) -> int:
        """
        Devuelve la presición del reconocimiento.
        
        Returns:
            int: Presición del reconocimiento en porcentaje
            
        Note:
            Actualiza el contador en memoria (self.presicion)
        """
        return self.__presicion

    def obtener_taza_error(self) -> int:
        """
        Devuelve la taza de error del reconocimiento.
        
        Returns:
            int: Taza de error
            
        Note:
            Actualiza el contador en memoria (self.taza_error)
        """
        return self.__taza_error
    
    def obtener_efectividad(self) -> str:
        """
        Devuelve la efectividad del reconocimiento.
        
        Returns:
            str: Efectividad del reconocimiento
            
        Note:
            Actualiza el contador en memoria (self.efectividad)
        """
        return self.__efectividad

    def obtener_logs_usuario(self, nombre: str):
        """
        Devuelve todos los logs asociados a un usuario específico.
        
        Args:
            nombre (str): Nombre del usuario cuyos logs se desean consultar
            
        Returns:
            list: Lista de tuplas con todos los logs del usuario, ordenados por fecha descendente
            list: Lista vacía si el usuario no existe o no tiene logs
            
        Note:
            Los resultados se ordenan por fecha de más reciente a más antigua
        """
        id_usuario = self.__obtener_id_usuario(nombre.lower())
        if id_usuario is None:
            print(f"Usuario '{nombre}' no encontrado.")
            return []

        conn = self.__conexion()
        cursor = conn.cursor()
        sql = "SELECT * FROM logs WHERE id_usuario = %s ORDER BY fecha DESC"
        cursor.execute(sql, (id_usuario,))
        result = cursor.fetchall()
        conn.close()
        return result

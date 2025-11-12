from db.config import conectar

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
        self.intentos_totales = 0      # Número total de intentos registrados
        self.intentos_exitosos = 0     # Número de intentos exitosos (status_log = True/1)
        self.intentos_fallidos = 0     # Número de intentos fallidos (status_log = False/0)
        self.id_usuario = ""           # ID del usuario actual (se establece automáticamente)

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

    # ==========================
    # MÉTODOS DE REGISTRO
    # ==========================

    def registrar_log(self, nombre: str, status_log: bool) -> None:
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
        id_usuario = self.__obtener_id_usuario(nombre.lower())
        if id_usuario is None:
            print(f"Usuario '{nombre}' no encontrado en la base de datos.")
            return

        conn = self.__conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO logs (id_usuario, status_log) VALUES (%s, %s)"
        cursor.execute(sql, (id_usuario, status_log))
        conn.commit()
        conn.close()

        # Actualiza contadores en memoria
        self.intentos_totales += 1
        if status_log:
            self.intentos_exitosos += 1
        else:
            self.intentos_fallidos += 1

        print(f"Log registrado para '{nombre}' {'Exitoso' if status_log == 1 else 'Fallido'}.")

    # ==========================
    # MÉTODOS DE CONSULTA
    # ==========================
    
    def obtener_intentos(self) -> int:
        """
        Devuelve el total de intentos registrados en la base de datos.
        
        Returns:
            int: Número total de intentos registrados
            
        Note:
            Actualiza el contador en memoria (self.intentos_totales)
        """
        conn = self.__conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        result = cursor.fetchone()
        conn.close()
        self.intentos_totales = result[0] if result else 0
        return self.intentos_totales

    def obtener_intentos_exitosos(self) -> int:
        """
        Devuelve el total de intentos exitosos.
        
        Returns:
            int: Número de intentos con status_log = True/1
            
        Note:
            Actualiza el contador en memoria (self.intentos_exitosos)
        """
        conn = self.__conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs WHERE status_log = TRUE")
        result = cursor.fetchone()
        conn.close()
        self.intentos_exitosos = result[0] if result else 0
        return self.intentos_exitosos

    def obtener_intentos_fallidos(self) -> int:
        """
        Devuelve el total de intentos fallidos.
        
        Returns:
            int: Número de intentos con status_log = False/0
            
        Note:
            Actualiza el contador en memoria (self.intentos_fallidos)
        """
        conn = self.__conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs WHERE status_log = FALSE")
        result = cursor.fetchone()
        conn.close()
        self.intentos_fallidos = result[0] if result else 0
        return self.intentos_fallidos

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
from reconocimiento.registro_logs import Logs

logs = Logs() ## Llamamos a clase
logs.fetch_data() ## trae todos los datos necesarios para que la clase funcione


intentos = logs.obtener_intentos_totales() # imprime los intentos globales
print(f"intentos totoles {intentos}")

intentos_exitosos = logs.obtener_intentos_exitosos() # Imprime los intentos exitosos
print(f"intentos exitosos {intentos_exitosos}")

intentos_fallidos = logs.obtener_intentos_fallidos() # Imprime los intentos fallidos
print(f"intentos fallidos {intentos_fallidos}")

presicion = logs.obtener_presicion() # Imprime en porcentaje la presición del programa
print(f"presicion {presicion} %")

taza_error = logs.obtener_taza_error() # Imprime en porcentaje la taza de error
print(f"taza error {taza_error} %")

efecitividad = logs.obtener_efectividad() # Imprime la efectividad con una medida de likert
print(f"efectividad {efecitividad} ")










from reconocimiento.registro_logs import Logs

logs = Logs()
registro = logs.registrar_log("Brandon", False)
print(registro)

intentos = logs.obtener_intentos()
print(f"intentos totoles {intentos}")

intentos_exitosos = logs.obtener_intentos_exitosos()
print(f"intentos exitosos {intentos_exitosos}")

intentos_fallidos = logs.obtener_intentos_fallidos()
print(f"intentos fallidos {intentos_fallidos}")





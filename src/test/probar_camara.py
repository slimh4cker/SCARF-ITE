# Archivo para probar la conexión a una cámara IP usando OpenCV
# Se tiene qeu remplazar URL_CAMARA con la URL de la cámara que se desea probar
# Con ONVIF se puede obtener la URL de la cámara

import cv2

# Reemplaza con la URL de tu cámara (ejemplo con rtsp)
URL_CAMARA = "rtsp://camara:Password1@140.10.0.133/user=admin_password=tlJwpbo6_channel=0_stream=0&onvif=0.sdp?real_stream"

# Objeto de captura de video
cap = cv2.VideoCapture(URL_CAMARA)

# Verificar si la conexión fue exitosa
if not cap.isOpened():
    print("Error: No se pudo conectar al stream de la cámara.")
else:
    print("Conexión exitosa. Presiona 'q' para salir.")
    while True:
        # Leer frame por frame
        ret, frame = cap.read()
        
        # Si el frame se leyó correctamente (ret es True)
        if ret:
            # Mostrar el frame
            cv2.imshow('EASYTAO Stream', frame)

            # Detener el bucle si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Fin del stream o error de lectura.")
            break

# Liberar el objeto de captura y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
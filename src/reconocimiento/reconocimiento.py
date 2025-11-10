""" # Código para reconocer rostros en vivo
import cv2
import face_recognition
import numpy as np
import json
from db.config import conectar
import time

THRESHOLD = 0.45  # Ajustable entre 0.35 y 0.6 según precisión deseada
MUESTRAS_VIVO = 5  # Número de encodings que promediamos antes de decidir

def cargar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, embedding FROM usuarios")
    data = []
    for id, nombre, emb_json in cursor.fetchall():
        emb = np.array(json.loads(emb_json))
        data.append((id, nombre, emb))
    conn.close()
    return data

def reconocer():
    print("Preione 'q' para salir")
    usuarios = cargar_usuarios()
    print(f"[ℹ] Se cargaron {len(usuarios)} usuarios desde la base de datos.")

    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("rtsp://mffe:mn333w@140.10.2.9:554/12")
    #cv2.namedWindow("Reconocimiento Facial", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Reconocimiento Facial", 800, 600)
    


    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame, intentando reconectar...")
            time.sleep(1)
            continue

            

        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for (top, right, bottom, left), enc in zip(faces, encodings):
            name = "DESCONOCIDO"
            color = (0, 0, 255)
            label = "ACCESO DENEGADO"

            if len(usuarios) > 0:
                # Tomamos varias muestras en vivo para mayor confiabilidad
                muestras = []
                for i in range(MUESTRAS_VIVO):
                    muestras.append(enc)
                # Calculamos la distancia mínima entre las muestras y los usuarios
                distancias = []
                for u in usuarios:
                    d_min = min([np.linalg.norm(u[2] - m) for m in muestras])
                    distancias.append(d_min)

                idx = np.argmin(distancias)
                if distancias[idx] < THRESHOLD:
                    name = usuarios[idx][1]
                    color = (0, 255, 0)
                    label = f"ACCESO PERMITIDO: {name}"

            # Redimensionar coordenadas para el frame original
            top *= 2; right *= 2; bottom *= 2; left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Aviso al usuario
            cv2.putText(frame, f"Muestra en vivo: {len(muestras)}/{MUESTRAS_VIVO}", 
                        (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.putText(frame, "Mantente mirando la camara", 
                        (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        cv2.imshow("Reconocimiento Facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    reconocer() """

# Codigo para reconocer rostros en vivo con camara IP
import cv2
import face_recognition
import numpy as np
import json
from db.config import conectar
import time

THRESHOLD = 0.45   # Ajustable entre 0.35 y 0.6 segun precision deseada
MUESTRAS_VIVO = 5  # Numero de encodings que promediamos antes de decidir

def cargar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, embedding FROM usuarios")
    data = []
    for id, nombre, emb_json in cursor.fetchall():
        emb = np.array(json.loads(emb_json))
        data.append((id, nombre, emb))
    conn.close()
    return data

def reconocer():
    print("Presiona 'q' para salir")
    usuarios = cargar_usuarios()
    print(f"[ℹ] Se cargaron {len(usuarios)} usuarios desde la base de datos.")

    # Si quieres usar la webcam, comenta la linea RTSP y descomenta la de abajo
    cap = cv2.VideoCapture(0)

    # Camara IP (usa el canal /12 si /11 va muy lento)
    #cap = cv2.VideoCapture("rtsp://mffe:mn333w@140.10.2.9:554/11")

    # Configuracion para mejorar rendimiento y calidad
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Ventana de tamaño controlado
    cv2.namedWindow("Reconocimiento Facial", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Reconocimiento Facial", 800, 600)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame, intentando reconectar...")
            time.sleep(1)
            continue

        # Reducir el tamaño a la mitad para detección más rápida
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for (top, right, bottom, left), enc in zip(faces, encodings):
            name = "DESCONOCIDO"
            color = (0, 0, 255)
            label = "ACCESO DENEGADO"

            if len(usuarios) > 0:
                muestras = [enc for _ in range(MUESTRAS_VIVO)]

                distancias = []
                for u in usuarios:
                    d_min = min([np.linalg.norm(u[2] - m) for m in muestras])
                    distancias.append(d_min)

                idx = np.argmin(distancias)
                if distancias[idx] < THRESHOLD:
                    name = usuarios[idx][1]
                    color = (0, 255, 0)
                    label = f"ACCESO PERMITIDO: {name}"

            # Escalamos las coordenadas al tamaño original
            top *= 2; right *= 2; bottom *= 2; left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Mensajes informativos
            cv2.putText(frame, f"Muestra en vivo: {len(muestras)}/{MUESTRAS_VIVO}",
                        (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, "Mantente mirando la camara",
                        (10, frame.shape[0] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Reconocimiento Facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    reconocer()

# Codigo para reconocimiento facial en vivo con camara IP (optimizado y estable)
import cv2
import face_recognition
import numpy as np
import json
from db.config import conectar
import time

THRESHOLD = 0.45
FRAME_SKIP = 5
RESIZE_FACTOR = 0.25
MEMORIA_SEGUNDOS = 3  # <- Segundos que se mantiene el acceso verde

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

    url = "rtsp://mffe:mn333w@140.10.2.9:554/12"
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    cv2.namedWindow("Reconocimiento Facial", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Reconocimiento Facial", 800, 600)

    frame_count = 0
    ultimo_reconocido = None
    tiempo_reconocido = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ No se pudo leer frame, intentando reconectar...")
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(url)
            continue

        frame_count += 1

        # Mostrar directo si no toca procesar este frame
        if frame_count % FRAME_SKIP != 0:
            # Si hay un rostro recordado, seguir mostrando su recuadro verde
            if ultimo_reconocido and time.time() - tiempo_reconocido < MEMORIA_SEGUNDOS:
                cv2.putText(frame, f"ACCESO PERMITIDO: {ultimo_reconocido}", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Reconocimiento Facial", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # Procesamos el frame
        small = cv2.resize(frame, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        reconocido = False

        for (top, right, bottom, left), enc in zip(faces, encodings):
            name = "DESCONOCIDO"
            color = (0, 0, 255)
            label = "ACCESO DENEGADO"

            if usuarios:
                distancias = [np.linalg.norm(u[2] - enc) for u in usuarios]
                idx = np.argmin(distancias)
                if distancias[idx] < THRESHOLD:
                    name = usuarios[idx][1]
                    color = (0, 255, 0)
                    label = f"ACCESO PERMITIDO: {name}"
                    reconocido = True
                    ultimo_reconocido = name
                    tiempo_reconocido = time.time()

            scale = int(1 / RESIZE_FACTOR)
            top *= scale
            right *= scale
            bottom *= scale
            left *= scale

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Si no detecta pero hubo uno hace poco, lo mantenemos
        if not reconocido and ultimo_reconocido and time.time() - tiempo_reconocido < MEMORIA_SEGUNDOS:
            cv2.putText(frame, f"ACCESO PERMITIDO: {ultimo_reconocido}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Reconocimiento Facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    reconocer()

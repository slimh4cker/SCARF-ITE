# Código para reconocer rostros en vivo
import cv2
import face_recognition
import numpy as np
import json
from db.config import conectar

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

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
    reconocer()


""""
import cv2
import face_recognition
import numpy as np
import json
from config import conectar
import dlib
from scipy.spatial import distance

THRESHOLD = 0.45       # Distancia máxima para considerar que es el mismo usuario
MUESTRAS_VIVO = 5      # Número de encodings que promediamos antes de decidir

# Función para cargar usuarios desde la base de datos
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

# Función para calcular relación de ojos (EAR) para parpadeo
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def reconocer():
    usuarios = cargar_usuarios()
    print("Presione 'q' para salir")
    print(f"[ℹ] Se cargaron {len(usuarios)} usuarios desde la base de datos.")

    # Inicializar detector de rostro y puntos faciales para parpadeo
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    cap = cv2.VideoCapture(0)
    encodings_buffer = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        # Detectar parpadeo
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        blink_detected = False
        for rect in rects:
            shape = predictor(gray, rect)
            shape_np = np.zeros((68, 2), dtype="int")
            for i in range(68):
                shape_np[i] = (shape.part(i).x, shape.part(i).y)

            leftEye = shape_np[42:48]
            rightEye = shape_np[36:42]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            if ear < 0.25:  # Ajusta este umbral si quieres
                blink_detected = True

        for (top, right, bottom, left), enc in zip(faces, encodings):
            encodings_buffer.append(enc)
            if len(encodings_buffer) > MUESTRAS_VIVO:
                encodings_buffer.pop(0)

            name = "DESCONOCIDO"
            color = (0, 0, 255)
            label = "ACCESO DENEGADO"

            if len(encodings_buffer) == MUESTRAS_VIVO:
                promedio_enc = np.mean(np.array(encodings_buffer), axis=0)
                if len(usuarios) > 0:
                    distancias = [np.linalg.norm(u[2] - promedio_enc) for u in usuarios]
                    idx = np.argmin(distancias)
                    if distancias[idx] < THRESHOLD and blink_detected:
                        name = usuarios[idx][1]
                        color = (0, 255, 0)
                        label = f"ACCESO PERMITIDO: {name}"

            # Escalar coordenadas al tamaño original
            top *= 2; right *= 2; bottom *= 2; left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Reconocimiento Facial", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    reconocer()
"""
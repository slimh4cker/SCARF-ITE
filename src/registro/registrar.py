# Código de registro de usuarios 

import cv2
import face_recognition
import numpy as np
import json
import time
from db.config import conectar

def guardar_embedding(nombre, embedding):
    conn = conectar()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nombre, embedding) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, json.dumps(embedding.tolist())))
    conn.commit()
    conn.close()
    print(f"[✔] Usuario '{nombre}' registrado correctamente.")

def registrar_usuario():
    nombre = input("Nombre de la persona a registrar: ")
    cap = cv2.VideoCapture(0)
    muestras = []

    print("Presiona 's' para capturar una muestra del rostro (5 necesarias).")
    print("Preione 'q' para salir")
    while len(muestras) < 5:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, f"Muestras: {len(muestras)}/5", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Registro", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            if len(faces) == 0:
                print("No se detecto ningun rostro.")
                continue
            encodings = face_recognition.face_encodings(rgb, faces)
            muestras.append(encodings[0])
            print(f"Muestra {len(muestras)} guardada.")
            time.sleep(0.5)

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(muestras) > 0:
        promedio = np.mean(np.array(muestras), axis=0)
        guardar_embedding(nombre, promedio)
    else:
        print("No se registraron muestras.")

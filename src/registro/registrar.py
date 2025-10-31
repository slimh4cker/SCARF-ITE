# Código de registro de usuarios 
import cv2
# registrar.py
# Código de registro de usuarios desde carpeta de imágenes

import face_recognition
import numpy as np
import json
import os
from db.config import conectar
from dotenv import load_dotenv

load_dotenv()

IMAGE_PATH = os.getenv('IMAGE_PATH')

def guardar_embedding(nombre, embedding):
    """Guarda el embedding del usuario en la base de datos"""
    conn = conectar()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nombre, embedding) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, json.dumps(embedding.tolist())))
    conn.commit()
    conn.close()
    print(f" Usuario '{nombre}' registrado correctamente.")

def registrar_usuario():

    # Cargar clasificador Haar para detección de rostros
    haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector_rostros = cv2.CascadeClassifier(haar_path)

    carpetas = [d for d in os.listdir(IMAGE_PATH) if os.path.isdir(os.path.join(IMAGE_PATH, d))]
    print(f"📁 Se encontraron {len(carpetas)} carpetas para procesar.\n")

    for persona in carpetas:
        ruta_persona = os.path.join(IMAGE_PATH, persona)
        print(f"\n👤 Procesando a {persona}...")

        for archivo in os.listdir(ruta_persona):
            if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                ruta_imagen = os.path.join(ruta_persona, archivo)
                print(f"→ Analizando {archivo}...")

                imagen = cv2.imread(ruta_imagen)
                if imagen is None:
                    print(f"[⚠️] No se pudo leer {archivo}")
                    continue

                # Reducción de tamaño (reduce carga en la Raspberry)
                escala = 0.5
                imagen = cv2.resize(imagen, (0, 0), fx=escala, fy=escala)

                # Convertir a escala de grises para detección rápida
                gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

                # Detección con HaarCascade
                rostros = detector_rostros.detectMultiScale(
                    gris,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(80, 80)  # tamaño mínimo de rostro
                )

                if len(rostros) == 0:
                    print(f"[❌] No se detectó rostro en {archivo}.")
                    continue

                for (x, y, w, h) in rostros:
                    # Recortar rostro y convertir a RGB
                    rostro = imagen[y:y+h, x:x+w]
                    rostro_rgb = cv2.cvtColor(rostro, cv2.COLOR_BGR2RGB)

                    # Obtener encoding con face_recognition
                    encodings = face_recognition.face_encodings(rostro_rgb)
                    if encodings:
                        promedio = np.mean(np.array(encodings), axis=0)
                        print(f"[✔] Rostro detectado en {archivo}. Guardando embedding...")
                        guardar_embedding(persona, promedio)
                    else:
                        print(f"[⚠️] No se pudo generar encoding para {archivo}.")

    print("\n✅ Registro desde carpetas completado con HaarCascade + FaceRecognition.")

if __name__ == "__main__":
    registrar_usuario()

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
    

    carpetas = [d for d in os.listdir(IMAGE_PATH) if os.path.isdir(os.path.join(IMAGE_PATH, d))]
    print(f"Se encontraron {len(carpetas)} carpetas para procesar.\n")

    for persona in carpetas:
        ruta_persona = os.path.join(IMAGE_PATH, persona)
        print(f"Procesando a {persona}...")

        for archivo in os.listdir(ruta_persona):
            if archivo.lower().endswith((".jpg", ".png", ".jpeg")):
                ruta_imagen = os.path.join(ruta_persona, archivo)

                # Cargar imagen y convertir a RGB
                imagen = face_recognition.load_image_file(ruta_imagen)
                imagen_rgb = imagen[:, :, ::-1]  # Asegura formato RGB

                # Reducir tamaño si es muy grande (mejor rendimiento)
                if imagen_rgb.shape[0] > 1000:
                    imagen_rgb = cv2.resize(imagen_rgb, (0, 0), fx=0.5, fy=0.5)

                # Intentar detección con CNN (más preciso)
                try:
                    faces = face_recognition.face_locations(imagen_rgb, model="cnn")
                except Exception as e:
                    print(f"Error usando modelo CNN ({e}), probando con HOG...")
                    faces = face_recognition.face_locations(imagen_rgb, model="hog")

                print(f"Detecciones: {faces}")

                if not faces:
                    print(f"No se detectó rostro en {archivo}.")
                    continue

                # Obtener encodings y promediar
                encodings = face_recognition.face_encodings(imagen_rgb, faces)
                if encodings:
                    promedio = np.mean(np.array(encodings), axis=0)
                    print(f"Rostro detectado en {archivo}. Guardando embedding...")
                    guardar_embedding(persona, promedio)
                else:
                    print(f"No se pudo generar encoding para {archivo}.")

    print("\nRegistro desde carpetas completado.")

if __name__ == "__main__":
    registrar_usuario()

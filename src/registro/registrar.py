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
    """
    Recorre todas las carpetas dentro de RUTA_FOTOS.
    Cada carpeta representa a una persona y contiene imágenes de su rostro.
    Se genera un embedding promedio por persona y se guarda en la base de datos.
    """

    if not os.path.exists(IMAGE_PATH):
        print(f" La ruta {RUTA_FOTOS} no existe.")
        return

    carpetas_personas = [
        os.path.join(IMAGE_PATH, carpeta)
        for carpeta in os.listdir(IMAGE_PATH)
        if os.path.isdir(os.path.join(IMAGE_PATH, carpeta))
    ]

    if not carpetas_personas:
        print(f"No se encontraron carpetas dentro de {IMAGE_PATH}.")
        return

    print(f"Se encontraron {len(carpetas_personas)} carpetas para procesar.\n")

    # Procesar cada persona
    for carpeta_persona in carpetas_personas:
        nombre_persona = os.path.basename(carpeta_persona)
        print(f"Procesando a {nombre_persona}...")

        embeddings_persona = []

        for archivo in os.listdir(carpeta_persona):
            if not archivo.lower().endswith((".jpg", ".png")):
                continue

            ruta_imagen = os.path.join(carpeta_persona, archivo)
            try:
                imagen = face_recognition.load_image_file(ruta_imagen)
                imagen = imagen[:, :, ::-1]
                faces = face_recognition.face_locations(imagen)
                print(f"{faces}")
                print(imagen.shape)

                if len(faces) == 0:
                    print(f"No se detectó rostro en {archivo}.")
                    continue

                encodings = face_recognition.face_encodings(imagen, faces)

                # Guardamos todos los encodings (una imagen puede tener más de un rostro)
                embeddings_persona.extend(encodings)

            except Exception as e:
                print(f" Error procesando {archivo}: {e}")

        if not embeddings_persona:
            print(f"No se obtuvieron embeddings para {nombre_persona}. Se omite.\n")
            continue

        # Calcular embedding promedio de todas las imágenes de la persona
        embedding_promedio = np.mean(np.array(embeddings_persona), axis=0)
        guardar_embedding(nombre_persona, embedding_promedio)

        print(f" Embedding guardado para {nombre_persona}.\n")

    print("Registro completo finalizado.\n")

if __name__ == "__main__":
    registrar_usuario()

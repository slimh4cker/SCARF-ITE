# Código de registro de usuarios 

import cv2
# registrar.py
# Código de registro de usuarios desde carpeta de imágenes

import face_recognition
import numpy as np
import json
import os
from db.config import conectar, RUTA_FOTOS

def guardar_embedding(nombre, embedding):
    """Guarda el embedding del usuario en la base de datos"""
    conn = conectar()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nombre, embedding) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, json.dumps(embedding.tolist())))
    conn.commit()
    conn.close()
    print(f"[✔] Usuario '{nombre}' registrado correctamente.")

def registrar_desde_carpeta():
    """
    Lee todas las imágenes desde la carpeta configurada en RUTA_FOTOS,
    genera embeddings y los guarda en la base de datos.
    """
    archivos = os.listdir(RUTA_FOTOS)
    if not archivos:
        print(f"No se encontraron archivos en {RUTA_FOTOS}")
        return

    for archivo in archivos:
        if archivo.lower().endswith((".jpg", ".png")):
            ruta_imagen = os.path.join(RUTA_FOTOS, archivo)
            nombre = os.path.splitext(archivo)[0]  # Nombre del usuario basado en el nombre del archivo

            print(f"[ℹ] Procesando {archivo}...")

            imagen = face_recognition.load_image_file(ruta_imagen)
            faces = face_recognition.face_locations(imagen)

            if len(faces) == 0:
                print(f"No se detectó ningún rostro en {archivo}. Se omite.")
                continue

            encodings = face_recognition.face_encodings(imagen, faces)
            promedio = np.mean(np.array(encodings), axis=0)
            guardar_embedding(nombre, promedio)

    print("Registro desde carpeta completado.")

if __name__ == "__main__":
    registrar_desde_carpeta()


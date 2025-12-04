# registro/registrar.py
import cv2
import face_recognition
import numpy as np
import json
import os
from db.config import conectar
from dotenv import load_dotenv

load_dotenv()

IMAGE_PATH = os.getenv('IMAGE_PATH')

def guardar_embedding(nombre, embedding, log_callback=print):
    """Guarda el embedding del usuario en la base de datos"""
    try:
        log_callback(f"🔄 Conectando a la base de datos para '{nombre}'...")
        conn = conectar()
        cursor = conn.cursor()
        sql = "INSERT INTO usuarios (nombre, embedding) VALUES (%s, %s)"
        cursor.execute(sql, (nombre, json.dumps(embedding.tolist())))
        conn.commit()
        conn.close()
        log_callback(f" Usuario '{nombre}' registrado correctamente en BD.")
    except Exception as e:
        log_callback(f" Error de BD al guardar {nombre}: {e}")


def registrar_usuario(log_callback=None, progress_callback=None):
    """
    log_callback: función para enviar texto a la UI (reemplaza a print)
    progress_callback: función para enviar un float (0.0 a 1.0) a la barra de progreso
    """
    
    # Si no se pasan callbacks (ej. ejecutando desde consola), usamos print
    if log_callback is None:
        log_callback = print

    log_callback("🚀 Iniciando proceso de registro facial...")
    
    # Cargar clasificador Haar para detección de rostros
    log_callback("📁 Cargando clasificador Haar para detección de rostros...")
    haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector_rostros = cv2.CascadeClassifier(haar_path)
    
    if detector_rostros.empty():
        log_callback(" Error: No se pudo cargar el clasificador Haar")
        return
    else:
        log_callback(" Clasificador Haar cargado correctamente")

    if not os.path.exists(IMAGE_PATH):
        log_callback(f" Error: No existe la ruta {IMAGE_PATH}")
        return
    else:
        log_callback(f" Ruta de imágenes verificada: {IMAGE_PATH}")

    carpetas = [d for d in os.listdir(IMAGE_PATH) if os.path.isdir(os.path.join(IMAGE_PATH, d))]
    total_carpetas = len(carpetas)
    
    if total_carpetas == 0:
        log_callback("  No se encontraron carpetas de usuarios para procesar")
        return
    
    total_archivos = 0
    for persona in carpetas:
        ruta_persona = os.path.join(IMAGE_PATH, persona)
        archivos = os.listdir(ruta_persona)
        imagenes = [a for a in archivos if a.lower().endswith((".jpg", ".jpeg", ".png"))]
        total_archivos += len(imagenes)

    
    # Contar el número total de imágenes para el progreso
    total_imagenes = 0
    imagenes_por_carpeta = {}
    
    for persona in carpetas:
        ruta_persona = os.path.join(IMAGE_PATH, persona)
        archivos = os.listdir(ruta_persona)
        imagenes = [a for a in archivos if a.lower().endswith((".jpg", ".jpeg", ".png"))]
        imagenes_por_carpeta[persona] = len(imagenes)
        total_imagenes += len(imagenes)
    
    if total_imagenes == 0:
        log_callback("  No se encontraron imágenes para procesar")
        return
        
    log_callback(f"📊 Se encontraron {total_carpetas} carpetas con {total_imagenes} imágenes en total")
    log_callback("=" * 50)

    # Variables para el progreso
    imagenes_procesadas = 0
    
    for i, persona in enumerate(carpetas):
        ruta_persona = os.path.join(IMAGE_PATH, persona)
        log_callback(f"\n👤 Procesando usuario: '{persona}'...")
        log_callback(f"📂 Carpeta: {ruta_persona}")
        
        embeddings_de_la_persona = [] 

        archivos = os.listdir(ruta_persona)
        imagenes_encontradas = [a for a in archivos if a.lower().endswith((".jpg", ".jpeg", ".png"))]
        
        if not imagenes_encontradas:
            log_callback(f"  No se encontraron imágenes en la carpeta de '{persona}'")
            continue
            
        log_callback(f"🖼️  Encontradas {len(imagenes_encontradas)} imágenes para procesar")

        n = 1
        for j, archivo in enumerate(imagenes_encontradas):
            ruta_imagen = os.path.join(ruta_persona, archivo)
            log_callback(f"   📷 Analizando imagen {j+1}/{len(imagenes_encontradas)}: {archivo}")

            imagen = cv2.imread(ruta_imagen)
            if imagen is None:
                log_callback(f"    No se pudo leer la imagen: {archivo}")
                # Aún así contamos esta imagen como procesada
                imagenes_procesadas += 1
                if progress_callback:
                    progress_callback(imagenes_procesadas / total_imagenes)
                continue

            # Reducción de tamaño
            escala = 0.5
            try:
                imagen_redimensionada = cv2.resize(imagen, (0, 0), fx=escala, fy=escala)
                log_callback(f"   🔄 Imagen redimensionada a escala {escala}")
                imagen = imagen_redimensionada
            except cv2.error as e:
                log_callback(f"    Error al redimensionar {archivo}: {e}")
                imagenes_procesadas += 1
                if progress_callback:
                    progress_callback(imagenes_procesadas / total_imagenes)
                continue
                    
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            log_callback("   ⚫ Convertida a escala de grises")

            # Detección con HaarCascade
            log_callback("   🔍 Buscando rostros en la imagen...")
            rostros = detector_rostros.detectMultiScale(
                gris,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80)
            )

            if len(rostros) == 0:
                log_callback("     No se detectaron rostros en esta imagen")
            else:
                log_callback(f"    Se detectaron {len(rostros)} rostro(s) en la imagen")

            for k, (x, y, w, h) in enumerate(rostros):
                log_callback(f"   👁️  Procesando rostro {n}/{total_archivos}")
                n += 1
                rostro = imagen[y:y+h, x:x+w]
                rostro_rgb = cv2.cvtColor(rostro, cv2.COLOR_BGR2RGB)
                
                encodings = face_recognition.face_encodings(rostro_rgb) 
                
                if encodings:
                    embeddings_de_la_persona.append(encodings[0])
                    log_callback(f"    Encoding facial generado exitosamente (rostro {k+1})")
                else:
                    log_callback(f"    No se pudo generar encoding para el rostro {k+1}")

            # Actualizar progreso después de procesar cada imagen
            imagenes_procesadas += 1
            if progress_callback:
                progreso_actual = imagenes_procesadas / total_imagenes
                progress_callback(progreso_actual)
                log_callback(f"   📊 Progreso general: {progreso_actual*100:.1f}% ({imagenes_procesadas}/{total_imagenes} imágenes)")

        # Procesamiento final del usuario
        if not embeddings_de_la_persona:
            log_callback(f" No se encontraron embeddings válidos para '{persona}'. Usuario omitido.")
            continue 

        log_callback(f"📈 Calculando embedding promedio para '{persona}'...")
        log_callback(f"   📊 Total de embeddings generados: {len(embeddings_de_la_persona)}")
        
        promedio_total = np.mean(np.array(embeddings_de_la_persona), axis=0)
        log_callback(f"    Embedding promedio calculado (dimensión: {promedio_total.shape})")
        
        log_callback(f"💾 Guardando embedding en base de datos para '{persona}'...")
        guardar_embedding(persona, promedio_total, log_callback)
        
        log_callback(f" Usuario '{persona}' procesado exitosamente")
        log_callback("-" * 40)

    # Proceso completado
    if progress_callback:
        progress_callback(1.0)
        
    log_callback("🎉 Proceso de registro completado!")
    log_callback(f"📋 Resumen: {total_carpetas} usuarios procesados, {total_imagenes} imágenes analizadas")
    log_callback(" Sistema listo para reconocimiento facial")
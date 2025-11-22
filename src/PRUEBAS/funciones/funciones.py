
# ======================== LIBRERIAS ========================
import cv2
from dotenv import load_dotenv
import os
import time
import face_recognition
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk
from db.config import conectar  # tu conexion
import json
import threading, asyncio
import librerias.comunicador
from reconocimiento.registro_logs import Logs
import threading



load_dotenv()
logs = Logs()

url = os.getenv("url")  # URL para poder conectarse a la camara de andres o 0 para local

ruta_intrusos = os.getenv("INTRUSOS_PATH")
if not ruta_intrusos:
    raise Exception("Falta la variable de entorno INTRUSOS_PATH en el archivo .env")
ruta_intrusos = ruta_intrusos.strip()
ruta_intrusos = os.path.normpath(ruta_intrusos)


# ========================================================= FUNCIONES DE CAMARA =======================================================

# ======================== FUNCION PARA GUARDAR FOTOS ========================
def guardar_foto(self, frame):
    carpeta = ruta_intrusos
    ahora = time.time()
    if ahora - getattr(self, "ultimo_guardado", 0) < int(os.getenv("COOLDOWN_DETECTION")):
        return
    self.ultimo_guardado = ahora
    nombre = time.strftime("intruso_%Y%m%d_%H%M%S.jpg")
    logs.ejecutar(False)
    ruta = os.path.join(carpeta, nombre)
    try:
        cv2.imwrite(ruta, frame)
        print("Foto de intruso guardada en:", ruta)
    except Exception as e:
        print("Error guardando foto:", e)


# ======================== CAMARA HELPERS ========================

def start_camera(self):
    """
    Inicia la camara y el loop de video. Protegemos contra múltiples llamadas.
    """
    # si ya está en marcha no hacemos nada
    if getattr(self, "mostrar_video", False):
        return

    # marca que debe mostrarse video
    self.mostrar_video = True

    # abrir camara si no está abierta
    try:
        if getattr(self, "cap", None) is None or not getattr(self.cap, "isOpened", lambda: False)():
            # intenta abrir la url (o 0 si quieres la cam local)
            self.cap = cv2.VideoCapture(url)
    except Exception as e:
        print("Error al abrir la camara:", e)
        self.cap = None

    # cancelar job previo si quedo alguno (seguridad)
    try:
        if getattr(self, "_video_job", None) is not None:
            try:
                self.after_cancel(self._video_job)
            except Exception:
                pass
            self._video_job = None
    except Exception:
        pass

    # arrancar el loop de video mediante after para no bloquear la UI
    self._video_job = self.after(100, self.actualizar_video)


def stop_camera(self):
    """
    Detiene el loop y libera la camara; cancela el after si existe.
    """
    # indicamos que no se muestre video
    self.mostrar_video = False

    # cancelar cualquier job pendiente
    try:
        if getattr(self, "_video_job", None) is not None:
            try:
                self.after_cancel(self._video_job)
            except Exception:
                pass
            self._video_job = None
    except Exception as e:
        print("Warning stop_camera (cancel):", e)

    # liberar la camara
    try:
        if getattr(self, "cap", None) is not None:
            if getattr(self.cap, "isOpened", lambda: False)():
                try:
                    self.cap.release()
                except Exception as e:
                    print("Warning stop_camera (release):", e)
            self.cap = None
    except Exception as e:
        print("Warning stop_camera:", e)
        self.cap = None


def on_close(self):
    # al cerrar la app, liberar camara y salir
    try:
        self.stop_camera()
    except Exception:
        pass
    try:
        self.destroy()
    except Exception:
        pass

# ACTUALIZAR VIDEO (loop)


def actualizar_video(self):

    if not getattr(self, "mostrar_video", False):
        return

    # abrir camara si no está lista
    if self.cap is None or not self.cap.isOpened():
        self.cap = cv2.VideoCapture(url)
        self.after(200, self.actualizar_video)
        return

    ret, frame = self.cap.read()
    if not ret:
        self.after(50, self.actualizar_video)
        return

    # =============================
    #        ZOOM DIGITAL
    # =============================
    zoom = 1.3
    h, w, _ = frame.shape

    new_w = int(w / zoom)
    new_h = int(h / zoom)

    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    x2 = x1 + new_w
    y2 = y1 + new_h

    frame = frame[y1:y2, x1:x2]
    frame = cv2.resize(frame, (w, h))

    # inicializar contador
    if not hasattr(self, "frame_counter"):
        self.frame_counter = 0

    analizar = (self.frame_counter % 5 == 0)

    reconocido = False

    if analizar:
        try:
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(rgb_small)
            encs = face_recognition.face_encodings(rgb_small, faces)

            for (top, right, bottom, left), enc in zip(faces, encs):

                name = "DESCONOCIDO"
                color = (0, 0, 255)
                label = "ACCESO DENEGADO"

                if self.usuarios:
                    distancias = [np.linalg.norm(u[2] - enc) for u in self.usuarios]
                    idx = int(np.argmin(distancias))

                    if distancias[idx] < 0.45:
                        name = self.usuarios[idx][1]
                        id_usuario = self.usuarios[idx][0]
                        color = (0, 255, 0)
                        label = f"ACCESO PERMITIDO: {name}"

                        # guardar el acceso para seguir mostrando 3 segundos
                        self.ultimo_reconocido = name
                        self.tiempo_reconocido = time.time()
                        reconocido = True
                        logs.ejecutar(reconocido, id_usuario)
                        
                        print("Llamado correcto")


                    else:
                        # acceso denegado: guardar foto
                        guardar_foto(self, frame)

                # escalar coordenadas
                top *= 2; right *= 2; bottom *= 2; left *= 2

                # dibujar recuadro y texto individual de cada cara
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)

        except Exception as e:
            print("Error analizando:", e)

    # =============================
    #   ACCESO PERMITIDO (3s) - TEXTO CENTRADO ARRIBA
    # =============================

    if hasattr(self, "ultimo_reconocido") and self.ultimo_reconocido:
        if time.time() - self.tiempo_reconocido < 3:
            texto = f"ACCESO PERMITIDO: {self.ultimo_reconocido}"
            font = cv2.FONT_HERSHEY_SIMPLEX

            # Escalar tamaño del texto según el ancho del frame
            escala = max(.8, w / 700 * .8)  # base 1 para 700px de ancho, escala proporcional

            grosor = int(max(2, escala * 2))

            # Calcular tamaño del texto para centrar
            (text_w, text_h), baseline = cv2.getTextSize(texto, font, escala, grosor)
            pos_x = (w - text_w) // 2
            pos_y = text_h + 70  # 30 pixeles desde arriba (ajustable)

            # dibujar texto verde
            cv2.putText(frame, texto, (pos_x, pos_y), font, escala, (0, 255, 0), grosor)
            
            # enviar comando al arduino para abrir puerta
            if reconocido:
                puerto_arduino = os.getenv("puerto_arduino")
                if puerto_arduino:

                    def _bg_send():
                        try:
                            asyncio.run(librerias.comunicador.enviar_comando_arduino(puerto_arduino, "abrir_puerta", 9600))
                        except Exception as e:
                            print("Error enviando comando al arduino:", e)

                    threading.Thread(target=_bg_send, daemon=True).start()

                reconocido = False  # evitar múltiples envíos
            

        else:
            # ya pasaron los 3 segundos, borrar
            self.ultimo_reconocido = None

    # =============================
    #   MOSTRAR FRAME EN TKINTER
    # =============================
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_ctk = ctk.CTkImage(light_image=img_pil, size=(700, 400))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.image = img_ctk
    except Exception as e:
        print("Error mostrando frame:", e)

    self.frame_counter += 1
    self.after(10, self.actualizar_video)


# ======================== FUNCIONES DE BASES DE DATOS ========================

def cargar_usuarios(self):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, embedding FROM usuarios")
        data = []
        for id, nombre, emb_json in cursor.fetchall():
            emb = np.array(json.loads(emb_json))
            data.append((id, nombre, emb))
        conn.close()
        return data
    except Exception as e:
        print("Warning cargar_usuarios:", e)
        return []


# ======================== CURSOR ========================

def volver_con_cursor(self):
    # Cambiar cursor a modo "esperando"
    self.configure(cursor="wait")
    # Forzar a tkinter a refrescar el cursor AHORITA
    self.update_idletasks()

    # Regresar a pantalla de inicio
    self.mostrar_pantalla_inicio()

    # Desactivar cursor de espera despues de un pequeño delay
    self.after(500, lambda: self.configure(cursor=""))

"""  # ======================== LIBRERIAS ========================
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




load_dotenv()

url = os.getenv("url") #URL para poder conectarse a la camara de andres  

ruta_intrusos = os.getenv("INTRUSOS_PATH")

if not ruta_intrusos:
    raise Exception("Falta la variable de entorno INTRUSOS_PATH en el archivo .env")
ruta_intrusos = ruta_intrusos.strip()            # quita espacios al inicio y final
ruta_intrusos = os.path.normpath(ruta_intrusos)  # normaliza la ruta




# ========================================================= FUNCIONES DE CAMARA =======================================================

# ======================== FUNCION PARA GUARDAR FOTOS ========================
def guardar_foto(self, frame):

    carpeta = ruta_intrusos

    ahora = time.time()
    if ahora - self.ultimo_guardado < 8:
        return  
    self.ultimo_guardado = ahora

    nombre = time.strftime("intruso_%Y%m%d_%H%M%S.jpg")
    ruta = os.path.join(carpeta, nombre)

    cv2.imwrite(ruta, frame)
    print("Foto de intruso guardada en:", ruta)





# ======================== CAMARA HELPERS ========================

# -------------------- ESTA FUNCION SE ENCARGA DE INICIAR LA CAMARA  --------------------
def start_camera(self):
    # intenta reabrir la camara si es necesario
    if getattr(self, "cap", None) is None or not getattr(self.cap, "isOpened", lambda: False)():
        try:
            self.cap = cv2.VideoCapture(url) #Camara de andres
            #self.cap = cv2.VideoCapture(0)
        except Exception as e:
            print("Error al abrir la camara:", e)
            self.cap = None
    self.mostrar_video = True
    # arrancar el loop de video mediante after para no bloquear la UI
    self.after(100, self.actualizar_video)


# -------------------- ESTA FUNCION SE ENCARGA DE DETENER LA CAMARA CUANDO ENTRA A ANALITICAS --------------------

def stop_camera(self):
    # detener el loop y liberar la camara
    self.mostrar_video = False
    try:
        if getattr(self, "cap", None) is not None:
            if getattr(self.cap, "isOpened", lambda: False)():
                try:
                    self.cap.release()
                except Exception:
                    pass
            self.cap = None
    except Exception as e:
        print("Warning stop_camera:", e)
        self.cap = None

# -------------------- ESTA FUNCION SE ENCARGA DE CERRAR LA CAMARA CUANDO TERMINA EL PROGRAMA --------------------

def on_close(self):
    # al cerrar la app, liberar camara y salir
    try:
        self.stop_camera()
    except Exception:
        pass
    self.destroy()


# -------------------- ESTA FUNCION SE ENCARGA DEl reconocimiento --------------------


# ACTUALIZAR VIDEO (loop)
def actualizar_video(self):
    # si no debemos mostrar video, salimos
    if not getattr(self, "mostrar_video", False):
        return
    # asegurarnos que la camara este abierta
    if getattr(self, "cap", None) is None or not getattr(self.cap, "isOpened", lambda: False)():
        try:
            self.cap = cv2.VideoCapture(url) #camara de andres
            #self.cap = cv2.VideoCapture(0)
        except Exception as e:
            print("Error reabriendo camara:", e)
            self.cap = None
        if self.cap is None or not getattr(self.cap, "isOpened", lambda: False)():
            self.after(500, self.actualizar_video)
            return
    # leer frame
    ret, frame = self.cap.read()
    if not ret or frame is None:
        self.after(100, self.actualizar_video)
        return
    try:
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)
        for (top, right, bottom, left), enc in zip(faces, encodings):
            name = "DESCONOCIDO"
            color = (0, 0, 255)
            label = "ACCESO DENEGADO"
            if len(self.usuarios) > 0:
                muestras = [enc for _ in range(5)]
                distancias = []
                for u in self.usuarios:
                    d_min = min([np.linalg.norm(u[2] - m) for m in muestras])
                    distancias.append(d_min)
                idx = np.argmin(distancias)
                if distancias[idx] < 0.45:
                    name = self.usuarios[idx][1]
                    color = (0, 255, 0)
                    label = f"ACCESO PERMITIDO: {name}"
                else:
                     # ==== GUARDAR FOTO SOOLO SI NO ES RECONOCIDO ====
                    self.guardar_foto(frame)   
            top *= 2; right *= 2; bottom *= 2; left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    except Exception as e:
        print("Warning en reconocimiento:", e)
    # ------ CONVERTIR A CTkImage (ya no PhotoImage) ------
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        # IMPORTANTE: especificar el size real del label
        img_ctk = ctk.CTkImage(light_image=img_pil, size=(600, 400))
        if hasattr(self, "lbl_video"):
            self.lbl_video.configure(image=img_ctk)
            self.lbl_video.image = img_ctk
    except Exception as e:
        print("Warning al mostrar frame:", e)
    # loop
    if self.mostrar_video:
        self.after(10, self.actualizar_video)


# ======================== FUNCIONES DE BASES DE DATOS ========================

# FUNCION PARA CARGAR LOS USUARIOS REGISTRADOS EN LA BASE DE DATOS
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

#Funcion para que el cursor represente la espera del cambio de pantalla
def volver_con_cursor(self):
    # Cambiar cursor a modo "esperando"
    self.configure(cursor="wait")
    # Forzar a tkinter a refrescar el cursor AHORITA
    self.update_idletasks()
    
    # Regresar a pantalla de inicio
    self.mostrar_pantalla_inicio()
    
    # Desactivar cursor de espera despues de un pequeño delay
    self.after(500, lambda: self.configure(cursor=""))
 """


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

load_dotenv()

url = os.getenv("url")  # URL para poder conectarse a la camara de andres

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
    if ahora - getattr(self, "ultimo_guardado", 0) < 10:
        return
    self.ultimo_guardado = ahora
    nombre = time.strftime("intruso_%Y%m%d_%H%M%S.jpg")
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

    # abrir camara si no esta lista
    if self.cap is None or not self.cap.isOpened():
        self.cap = cv2.VideoCapture(url)
        self.after(200, self.actualizar_video)
        return

    ret, frame = self.cap.read()
    if not ret:
        self.after(50, self.actualizar_video)
        return

    # =====================================================
    # --------------------- ZOOM DIGITAL -------------------
    # =====================================================
    zoom = 1.4  # entre 1.2 y 1.8
    h, w, _ = frame.shape

    new_w = int(w / zoom)
    new_h = int(h / zoom)

    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2
    x2 = x1 + new_w
    y2 = y1 + new_h

    frame = frame[y1:y2, x1:x2]
    frame = cv2.resize(frame, (w, h))
    # =====================================================

    # inicializar contador
    if not hasattr(self, "frame_counter"):
        self.frame_counter = 0

    analizar = (self.frame_counter % 5 == 0)

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
                    muestras = [enc for _ in range(3)]
                    distancias = []

                    for u in self.usuarios:
                        try:
                            d = min([np.linalg.norm(u[2] - m) for m in muestras])
                        except:
                            d = 999
                        distancias.append(d)

                    idx = int(np.argmin(distancias))

                    if distancias[idx] < 0.45:
                        name = self.usuarios[idx][1]
                        color = (0, 255, 0)
                        label = f"ACCESO PERMITIDO: {name}"
                    else:
                        self.guardar_foto(frame)

                top *= 2; right *= 2; bottom *= 2; left *= 2
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        except Exception as e:
            print("Error analizando:", e)

    # mostrar video
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_ctk = ctk.CTkImage(light_image=img_pil, size=(600, 400))
        self.lbl_video.configure(image=img_ctk)
        self.lbl_video.image = img_ctk
    except:
        pass

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

#POR EL MOMENTO YA NO DA ERRORES EN CUESTION DE LA CAMARA DE LA LAPTOP

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from registro.registrar import registrar_usuario
import cv2
import face_recognition
import numpy as np
import json
from PIL import Image, ImageTk
from reconocimiento.registro_logs import Logs
from db.config import conectar  # tu conexion

# ESTA ES LA QUE UTILIZA LA CAMARA DE LA COMPUTADORA (PARA PRUEBAS)
from reconocimiento.reconocimiento import reconocer

# Configuracion global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_NAVBAR = "#6DA9E4"
COLOR_FONDO = "#F5F7FA"
COLOR_BOTON = "#3A6D8C"
COLOR_BOTON_HOVER = "#2E4F6E"
COLOR_TEXTO = "#1A1A1A"

class SCARFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SCARF ITE - Reconocimiento Facial")
        self.geometry("900x500")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO)

        # no abrir la camara aun hasta que la interfaz este creada
        self.cap = None
        self.usuarios = self.cargar_usuarios()

        # bandera control del loop de video
        self.mostrar_video = False

        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color=COLOR_FONDO)
        self.container.pack(fill="both", expand=True)

        # crear pantalla inicial (esto tambien invoca start_camera)
        self.mostrar_pantalla_inicio()

    # -------------------- camara helpers --------------------
    def start_camera(self):
        # intenta reabrir la camara si es necesario
        if getattr(self, "cap", None) is None or not getattr(self.cap, "isOpened", lambda: False)():
            try:
                self.cap = cv2.VideoCapture(0)
            except Exception as e:
                print("Error al abrir la camara:", e)
                self.cap = None

        self.mostrar_video = True
        # arrancar el loop de video mediante after para no bloquear la UI
        self.after(100, self.actualizar_video)

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

    # -----------------------------------------------------------------
    # PANTALLA PRINCIPAL
    # -----------------------------------------------------------------
    def mostrar_pantalla_inicio(self):
        # cuando vamos a la pantalla inicio, asegurarnos de parar cualquier cosa previa
        # (no liberamos camara aqui porque lo hacemos en analytics antes de entrar)
        for widget in self.container.winfo_children():
            widget.destroy()

        # ---------------- NAVBAR SUPERIOR ----------------
        navbar = ctk.CTkFrame(self.container, fg_color=COLOR_NAVBAR, height=70)
        navbar.pack(side="top", fill="x")

        logo = ctk.CTkLabel(navbar, text="🔍", text_color="white", font=("Segoe UI Emoji", 32, "bold"))
        logo.place(x=20, rely=0.5, anchor="w")

        titulo_izq = ctk.CTkLabel(navbar, text="SCARF - ITE", text_color="white", font=("Segoe UI", 20, "bold"))
        titulo_izq.place(x=80, rely=0.5, anchor="w")

        titulo_centro = ctk.CTkLabel(navbar, text="Sistema de Control Automatico por Reconocimiento Facial",
                                     text_color="white", font=("Segoe UI", 13, "bold"))
        titulo_centro.place(relx=0.5, rely=0.5, anchor="center")

        # ---------------- PANEL INFERIOR (contenido) ----------------
        panel_contenido = ctk.CTkFrame(self.container, fg_color=COLOR_FONDO)
        panel_contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # Espacio para la camara
        espacio_camara = ctk.CTkFrame(panel_contenido, fg_color="#E8EDF2", corner_radius=10, width=500, height=360)
        espacio_camara.pack(side="left", fill="y", padx=(20, 0), pady=10)

        # label para mostrar el video
        self.lbl_video = ctk.CTkLabel(espacio_camara, text="")
        self.lbl_video.place(relx=0.5, rely=0.5, anchor="center")

        # Panel derecho con botones
        panel_derecho = ctk.CTkFrame(panel_contenido, fg_color=COLOR_FONDO)
        panel_derecho.pack(side="right", fill="both", expand=True, padx=(60, 20), pady=(0, 20))

        titulo = ctk.CTkLabel(panel_derecho, text="Registro de Usuario", text_color=COLOR_TEXTO,
                              font=("Segoe UI", 24, "bold"))
        titulo.pack(pady=(40, 30))

        boton_registrar = ctk.CTkButton(panel_derecho, text="Registrar Usuario", fg_color=COLOR_BOTON,
                                        hover_color=COLOR_BOTON_HOVER, corner_radius=20, width=220, height=50,
                                        font=("Segoe UI", 13, "bold"), text_color="white",
                                        command=lambda: messagebox.showinfo("Registro", "Funcionalidad aun no implementada."))
        boton_registrar.pack(pady=10)

        boton_analytics = ctk.CTkButton(panel_derecho, text="Ver Analytics", fg_color=COLOR_BOTON,
                                        hover_color=COLOR_BOTON_HOVER, corner_radius=20, width=220, height=50,
                                        font=("Segoe UI", 13, "bold"), text_color="white",
                                        command=self.mostrar_pantalla_analytics)
        boton_analytics.pack(pady=10)

        boton_salir = ctk.CTkButton(panel_derecho, text="Salir", fg_color="#B03A3A", hover_color="#802828",
                                   corner_radius=20, width=220, height=50, font=("Segoe UI", 13, "bold"),
                                   text_color="white", command=self.on_close)
        boton_salir.pack(pady=10)

        footer = ctk.CTkLabel(panel_derecho, text="Proyecto SCARF ITE © 2025", text_color="#7B7B7B",
                              font=("Segoe UI", 9))
        footer.pack(side="bottom", pady=10)

        # arrancar la camara aqui (ya existe self.lbl_video)
        self.start_camera()

    def on_close(self):
        # al cerrar la app, liberar camara y salir
        try:
            self.stop_camera()
        except Exception:
            pass
        self.destroy()

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

    # ACTUALIZAR VIDEO (loop)
    from customtkinter import CTkImage

    # ACTUALIZAR VIDEO (loop)
    def actualizar_video(self):
        # si no debemos mostrar video, salimos
        if not getattr(self, "mostrar_video", False):
            return

        # asegurarnos que la camara este abierta
        if getattr(self, "cap", None) is None or not getattr(self.cap, "isOpened", lambda: False)():
            try:
                self.cap = cv2.VideoCapture(0)
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


    #Funcion para que el cursor represente la espera del cambio de pantalla
    def volver_con_cursor(self):
        # Cambiar cursor a modo "esperando"
        self.configure(cursor="wait")

        # Forzar a tkinter a refrescar el cursor AHORITA
        self.update_idletasks()
        
        # Regresar a pantalla de inicio
        self.mostrar_pantalla_inicio()
        
        # Desactivar cursor de espera despues de un pequeño delay
        self.after(300, lambda: self.configure(cursor=""))

    # -----------------------------------------------------------------
    # PANTALLA DE ANALYTICS (con datos desde Logs)
    # -----------------------------------------------------------------
    def mostrar_pantalla_analytics(self):
        # primero detener la camara/loop para evitar que intente actualizar widgets destruidos
        self.stop_camera()

        # limpiamos la vista actual
        for widget in self.container.winfo_children():
            widget.destroy()

        panel = ctk.CTkFrame(self.container, fg_color=COLOR_FONDO)
        panel.pack(fill="both", expand=True, padx=20, pady=20)

        boton_volver = ctk.CTkButton(panel, text="← Volver", fg_color="#B0B0B0", hover_color="#8A8A8A",
                                     corner_radius=20, width=100, font=("Segoe UI", 11, "bold"),
                                     command=self.volver_con_cursor)
        boton_volver.pack(anchor="w", pady=(10, 0))

        titulo = ctk.CTkLabel(panel, text="Panel de Analiticas del Sistema", text_color=COLOR_TEXTO,
                              font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=(10, 20))

        # datos por defecto
        total_intentos = 0
        intentos_exitosos = 0
        intentos_fallidos = 0
        presicion = 0.0
        taza_error = 0.0
        efectividad = "N/A"

        try:
            logs = Logs()
            if hasattr(logs, "fetch_data"):
                logs.fetch_data()

            if hasattr(logs, "obtener_intentos_totales"):
                total_intentos = logs.obtener_intentos_totales() or 0
            if hasattr(logs, "obtener_intentos_exitosos"):
                intentos_exitosos = logs.obtener_intentos_exitosos() or 0
            if hasattr(logs, "obtener_intentos_fallidos"):
                intentos_fallidos = logs.obtener_intentos_fallidos() or 0
            if hasattr(logs, "obtener_presicion"):
                presicion = logs.obtener_presicion() or 0.0
            if hasattr(logs, "obtener_taza_error"):
                taza_error = logs.obtener_taza_error() or 0.0
            if hasattr(logs, "obtener_efectividad"):
                efectividad = logs.obtener_efectividad() or "N/A"

        except Exception as e:
            print("Warning: no se pudieron cargar los logs para Analytics:", e)

        frame_metricas = ctk.CTkFrame(panel, fg_color=COLOR_FONDO)
        frame_metricas.pack(pady=10)

        def crear_card(titulo_texto, valor, color):
            card = ctk.CTkFrame(frame_metricas, fg_color=color, corner_radius=15)
            card.pack(side="left", padx=15, ipadx=10, ipady=10)
            ctk.CTkLabel(card, text=titulo_texto, text_color="white", font=("Segoe UI", 13, "bold")).pack(pady=(5, 2))
            ctk.CTkLabel(card, text=str(valor), text_color="white", font=("Segoe UI", 22, "bold")).pack(pady=(2, 5))

        crear_card("Total de Intentos", total_intentos, "#6DA9E4")
        crear_card("Accesos Exitosos", intentos_exitosos, "#5E8AC7")
        crear_card("Accesos Fallidos", intentos_fallidos, "#E57373")

        frame_stats = ctk.CTkFrame(panel, fg_color="#E3ECF8", corner_radius=10)
        frame_stats.pack(pady=25, fill="x", padx=40)

        ctk.CTkLabel(frame_stats, text="📊 Estadisticas del Sistema", font=("Segoe UI", 14, "bold"),
                     text_color=COLOR_TEXTO).pack(pady=(10, 10))

        try:
            pres_text = f"Tasa de Error:     {float(taza_error):.2f} %"
        except Exception:
            pres_text = f"Tasa de Error:     {taza_error}"

        try:
            prec_text = f"Precision:          {float(presicion):.2f} %"
        except Exception:
            prec_text = f"Precision:          {presicion}"

        ctk.CTkLabel(frame_stats, text=pres_text, font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20)
        ctk.CTkLabel(frame_stats, text=prec_text, font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20)
        ctk.CTkLabel(frame_stats, text=f"Efectividad Global: {efectividad}", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(0, 10))

        grafico = ctk.CTkFrame(panel, fg_color="#D0D8E8", corner_radius=10, height=120)
        grafico.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(grafico, text="📈 (Aqui ira el grafico de desempeño del sistema)", font=("Segoe UI", 11, "italic"),
                     text_color="#555").pack(expand=True)

        footer = ctk.CTkLabel(panel, text="Proyecto SCARF ITE © 2025", text_color="#7B7B7B", font=("Segoe UI", 9))
        footer.pack(side="bottom", pady=10)


if __name__ == "__main__":
    app = SCARFApp()
    app.mainloop()

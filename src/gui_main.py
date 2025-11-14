import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from registro.registrar import registrar_usuario
import cv2
import face_recognition
import numpy as np
import json
from PIL import Image
from PIL import ImageTk

from db.config import conectar  # tu conexion


#ESTA ES LA QUE UTILIZA LA CAMARA DE LA COMPUTADORA (PARA PRUEBAS)
from reconocimiento.reconocimiento import reconocer

#ESTA ES LA QUE SE USA PARA LA CAMARA DE ANDRES
#from reconocimiento.rec import reconocer

# Configuración global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_NAVBAR = "#6DA9E4"
COLOR_FONDO = "#F5F7FA"
COLOR_BOTON = "#3A6D8C"
COLOR_BOTON_HOVER = "#2E4F6E"
COLOR_TEXTO = "#1A1A1A"

# ---------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------
class SCARFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SCARF ITE - Reconocimiento Facial")
        self.geometry("900x500")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO)

        self.cap = cv2.VideoCapture(0)  # o la camara IP
        self.usuarios = self.cargar_usuarios()



        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color=COLOR_FONDO)
        self.container.pack(fill="both", expand=True)

        self.mostrar_pantalla_inicio()
        self.actualizar_video()   # iniciar el video en el GUI


    # -----------------------------------------------------------------
    # PANTALLA PRINCIPAL
    # -----------------------------------------------------------------
    def mostrar_pantalla_inicio(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # ---------------- NAVBAR SUPERIOR ----------------
        navbar = ctk.CTkFrame(self.container, fg_color=COLOR_NAVBAR, height=70)
        navbar.pack(side="top", fill="x")

        # Icono izquierda
        logo = ctk.CTkLabel(
            navbar,
            text="🔍",
            text_color="white",
            font=("Segoe UI Emoji", 32, "bold")
        )
        logo.place(x=20, rely=0.5, anchor="w")

        # Texto SCARF ITE a la derecha del ícono
        titulo_izq = ctk.CTkLabel(
            navbar,
            text="SCARF - ITE",
            text_color="white",
            font=("Segoe UI", 20, "bold")
        )
        titulo_izq.place(x=80, rely=0.5, anchor="w")

        # Texto centrado
        titulo_centro = ctk.CTkLabel(
            navbar,
            text="Sistema de Control Automático por Reconocimiento Facial",
            text_color="white",
            font=("Segoe UI", 13, "bold")
        )
        titulo_centro.place(relx=0.5, rely=0.5, anchor="center")

        # ---------------- PANEL INFERIOR (contenido) ----------------
        panel_contenido = ctk.CTkFrame(self.container, fg_color=COLOR_FONDO)
        panel_contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # Espacio vacío para la cámara (a la izquierda, más grande)
        espacio_camara = ctk.CTkFrame(panel_contenido, fg_color="#E8EDF2", corner_radius=10, width=400, height=360)
        espacio_camara.pack(side="left", fill="y", padx=(20, 0), pady=10)

        self.lbl_video = ctk.CTkLabel(espacio_camara, text="")
        self.lbl_video.place(relx=0.5, rely=0.5, anchor="center")


        # Panel derecho con botones (subido un poco)
        panel_derecho = ctk.CTkFrame(panel_contenido, fg_color=COLOR_FONDO)
        panel_derecho.pack(side="right", fill="both", expand=True, padx=(60, 20), pady=(0, 20))

        titulo = ctk.CTkLabel(
            panel_derecho,
            text="Registro de Usuario",
            text_color=COLOR_TEXTO,
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=(40, 30))  # <-- Subido (antes 60,40)

        # Botones (igual estilo, texto en negritas)
        boton_registrar = ctk.CTkButton(
            panel_derecho,
            text="Registrar Usuario",
            fg_color=COLOR_BOTON,
            hover_color=COLOR_BOTON_HOVER,
            corner_radius=20,
            width=220,
            height=50,
            font=("Segoe UI", 13, "bold"),
            text_color="white",
            command=lambda: messagebox.showinfo("Registro", "Funcionalidad aún no implementada.")
        )
        boton_registrar.pack(pady=10)

        boton_analytics = ctk.CTkButton(
            panel_derecho,
            text="Ver Analytics",
            fg_color=COLOR_BOTON,
            hover_color=COLOR_BOTON_HOVER,
            corner_radius=20,
            width=220,
            height=50,
            font=("Segoe UI", 13, "bold"),
            text_color="white",
            command=self.mostrar_pantalla_analytics
        )
        boton_analytics.pack(pady=10)

        boton_salir = ctk.CTkButton(
            panel_derecho,
            text="Salir",
            fg_color="#B03A3A",
            hover_color="#802828",
            corner_radius=20,
            width=220,
            height=50,
            font=("Segoe UI", 13, "bold"),
            text_color="white",
            command=self.destroy
        )
        boton_salir.pack(pady=10)

        footer = ctk.CTkLabel(
            panel_derecho,
            text="Proyecto SCARF ITE © 2025",
            text_color="#7B7B7B",
            font=("Segoe UI", 9)
        )
        footer.pack(side="bottom", pady=10)


#FUNCION PARA CARGAR LOS USUARIOS REGISTRADOS EN LA BASE DE DATOS
    def cargar_usuarios(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, embedding FROM usuarios")
        data = []
        for id, nombre, emb_json in cursor.fetchall():
            emb = np.array(json.loads(emb_json))
            data.append((id, nombre, emb))
        conn.close()
        return data


    #ESTA FUNCION ES LA MAS IMPORTANTE, YA QUE ES LA QUE SE ENCARGA DE HACER EL RECONOCIMIENTO Y DAR ACCESO O NEGARLO
    def actualizar_video(self):
        THRESHOLD = 0.45
        MUESTRAS_VIVO = 5

        ret, frame = self.cap.read()
        if ret:

            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, faces)

            for (top, right, bottom, left), enc in zip(faces, encodings):

                name = "DESCONOCIDO"
                color = (0, 0, 255)
                label = "ACCESO DENEGADO"

                # comparar con usuarios
                if len(self.usuarios) > 0:
                    muestras = [enc for _ in range(MUESTRAS_VIVO)]
                    distancias = []

                    for u in self.usuarios:
                        d_min = min([np.linalg.norm(u[2] - m) for m in muestras])
                        distancias.append(d_min)

                    idx = np.argmin(distancias)
                    if distancias[idx] < THRESHOLD:
                        name = self.usuarios[idx][1]
                        color = (0, 255, 0)
                        label = f"ACCESO PERMITIDO: {name}"

                # regresar escala al frame original
                top *= 2; right *= 2; bottom *= 2; left *= 2
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # convertir para mostrar en tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

            self.lbl_video.configure(image=img)
            self.lbl_video.image = img

        self.after(10, self.actualizar_video)


    # -----------------------------------------------------------------
    # PANTALLA ANALYTICS
    # -----------------------------------------------------------------
    def mostrar_pantalla_analytics(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        panel = ctk.CTkFrame(self.container, fg_color=COLOR_FONDO)
        panel.pack(fill="both", expand=True, padx=20, pady=20)

        boton_volver = ctk.CTkButton(
            panel,
            text="← Volver",
            fg_color="#B0B0B0",
            hover_color="#8A8A8A",
            corner_radius=20,
            width=100,
            font=("Segoe UI", 11, "bold"),
            command=self.mostrar_pantalla_inicio
        )
        boton_volver.pack(anchor="w", pady=(10, 0))

        titulo = ctk.CTkLabel(
            panel,
            text="Panel de Analíticas del Sistema",
            text_color=COLOR_TEXTO,
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=(10, 20))

        frame_metricas = ctk.CTkFrame(panel, fg_color=COLOR_FONDO)
        frame_metricas.pack(pady=10)

        def crear_card(titulo, valor, color):
            card = ctk.CTkFrame(frame_metricas, fg_color=color, corner_radius=15)
            card.pack(side="left", padx=15, ipadx=10, ipady=10)
            ctk.CTkLabel(card, text=titulo, text_color="white", font=("Segoe UI", 13, "bold")).pack(pady=(5, 2))
            ctk.CTkLabel(card, text=str(valor), text_color="white", font=("Segoe UI", 22, "bold")).pack(pady=(2, 5))

        crear_card("Total de Intentos", 120, "#6DA9E4")
        crear_card("Accesos Exitosos", 105, "#5E8AC7")
        crear_card("Accesos Fallidos", 15, "#E57373")

        frame_stats = ctk.CTkFrame(panel, fg_color="#E3ECF8", corner_radius=10)
        frame_stats.pack(pady=25, fill="x", padx=40)

        ctk.CTkLabel(frame_stats, text="📊 Estadísticas del Sistema", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXTO).pack(pady=(10, 10))
        ctk.CTkLabel(frame_stats, text="Tasa de Error:     12.5%", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20)
        ctk.CTkLabel(frame_stats, text="Precisión:          87.5%", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20)
        ctk.CTkLabel(frame_stats, text="Efectividad Global: Alta", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(0, 10))

        grafico = ctk.CTkFrame(panel, fg_color="#D0D8E8", corner_radius=10, height=120)
        grafico.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(grafico, text="📈 (Aquí irá el gráfico de desempeño del sistema)", font=("Segoe UI", 11, "italic"), text_color="#555").pack(expand=True)

        footer = ctk.CTkLabel(
            panel,
            text="Proyecto SCARF ITE © 2025",
            text_color="#7B7B7B",
            font=("Segoe UI", 9)
        )
        footer.pack(side="bottom", pady=10)


# ---------------------------------------------------------------------
if __name__ == "__main__":
    app = SCARFApp()
    app.mainloop()
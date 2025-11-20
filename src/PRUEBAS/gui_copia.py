  #POR EL MOMENTO YA NO DA ERRORES EN CUESTION DE LA CAMARA DE LA LAPTOP

from tkinter import messagebox
import customtkinter as ctk

# LIBRERIAS DE FUNCIONES
from registro.registrar import registrar_usuario
from reconocimiento.registro_logs import Logs

import threading # PARA ANALIZAR IMAGENES SIN CONGELAR LA GUI

# ESTA ES LA QUE UTILIZA LA CAMARA DE LA COMPUTADORA (PARA PRUEBAS)
from reconocimiento.reconocimiento import reconocer

from funciones.funciones import (
    start_camera,
    stop_camera,
    on_close,
    actualizar_video,
    guardar_foto,
    cargar_usuarios,
    volver_con_cursor
)



from dotenv import load_dotenv
load_dotenv()



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
        #self.ultimo_recon = 0

        

      

        # no abrir la camara aun hasta que la interfaz este creada
        self.cap = None
        
        """   SCARFApp.start_camera = start_camera
        SCARFApp.stop_camera = stop_camera
        SCARFApp.on_close = on_close
        SCARFApp.actualizar_video = actualizar_video
        SCARFApp.guardar_foto = guardar_foto
        SCARFApp.cargar_usuarios = cargar_usuarios
        SCARFApp.volver_con_cursor = volver_con_cursor """


        self.usuarios = self.cargar_usuarios()   # primero carga usuarios
        self.ultimo_guardado = 0                 # inicializa contador
        # bandera control del loop de video
        self.mostrar_video = False

        # Contenedor principal
        self.container = ctk.CTkFrame(self, fg_color=COLOR_FONDO)
        self.container.pack(fill="both", expand=True)

        # crear pantalla inicial (esto tambien invoca start_camera)
        self.mostrar_pantalla_inicio() 
        #self.start_camera() 

        self.ultimo_reconocido = None
        self.tiempo_reconocido = 0
        self.MEMORIA_SEGUNDOS = 3  # mantener acceso permitido verde por 3 segundos


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
                                        command=self.registrar_usuario_window)
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
    
    def registrar_usuario_window(self):
        self.stop_camera()

        # Crear ventana modal más pequeña
        ventana_registro = ctk.CTkToplevel(self)
        ventana_registro.title("Procesando Registro")
        ventana_registro.geometry("400x200")  # Ventana más compacta
        ventana_registro.resizable(False, False)
        
        # Centrar la ventana en la pantalla
        ventana_registro.transient(self)
        ventana_registro.grab_set()
        
        # --- UI DE LA VENTANA MODAL COMPACTA ---
        titulo = ctk.CTkLabel(ventana_registro, text="Registrando Usuarios", 
                            font=("Segoe UI", 16, "bold"))
        titulo.pack(pady=(15, 10))

        # Frame para el estado actual (más compacto)
        frame_estado = ctk.CTkFrame(ventana_registro, fg_color="#F0F0F0", corner_radius=8)
        frame_estado.pack(fill="x", padx=20, pady=5)
        
        # Label para el estado actual (en lugar de Textbox grande)
        lbl_estado_titulo = ctk.CTkLabel(frame_estado, text="Estado actual:", 
                                    font=("Segoe UI", 11, "bold"), text_color="#555555")
        lbl_estado_titulo.pack(anchor="w", padx=10, pady=(8, 0))
        
        self.lbl_estado_actual = ctk.CTkLabel(frame_estado, text="Iniciando sistema de registro...", 
                                            font=("Segoe UI", 11), text_color="#333333",
                                            wraplength=350, height=30)
        self.lbl_estado_actual.pack(fill="x", padx=10, pady=(0, 8))

        # Barra de progreso más compacta
        lbl_progreso = ctk.CTkLabel(ventana_registro, text="Progreso:", 
                                font=("Segoe UI", 11))
        lbl_progreso.pack(pady=(10, 5))
        
        barra_progreso = ctk.CTkProgressBar(ventana_registro, width=350, height=12)
        barra_progreso.pack(pady=5)
        barra_progreso.set(0)

        # Botón cerrar
        btn_cerrar = ctk.CTkButton(ventana_registro, text="Cerrar", state="disabled", 
                                command=ventana_registro.destroy, fg_color="#B03A3A",
                                width=100, height=32)
        btn_cerrar.pack(pady=15)

        # --- FUNCIONES DE CALLBACK ---
        def callback_texto(mensaje):
            # Actualizar solo el texto del label con el mensaje actual
            def _update():
                self.lbl_estado_actual.configure(text=mensaje)
            self.after(0, _update)

        def callback_progreso(valor_0_a_1):
            self.after(0, lambda: barra_progreso.set(valor_0_a_1))

        # --- EJECUCIÓN EN HILO SECUNDARIO ---
        def proceso_en_background():
            try:
                # Llamamos a la función de registro con los callbacks
                registrar_usuario(log_callback=callback_texto, progress_callback=callback_progreso)
                callback_texto(" Proceso completado exitosamente")
            except Exception as e:
                callback_texto(f" Error: {str(e)}")
                import traceback
                print(traceback.format_exc())  # Para debugging en consola
            finally:
                # Habilitar botón de cerrar al terminar
                self.after(0, lambda: btn_cerrar.configure(state="normal", fg_color=COLOR_BOTON))
                # Recargar usuarios en memoria principal
                self.usuarios = self.cargar_usuarios()

        # Iniciamos el hilo
        hilo = threading.Thread(target=proceso_en_background)
        hilo.daemon = True
        hilo.start()
        
        # Centrar la ventana
        self.centrar_ventana(ventana_registro)

    def centrar_ventana(self, ventana):
        """Centra una ventana respecto a la ventana principal"""
        self.update_idletasks()
        ancho_ventana = ventana.winfo_width()
        alto_ventana = ventana.winfo_height()
        x = (self.winfo_width() // 2) - (ancho_ventana // 2) + self.winfo_x()
        y = (self.winfo_height() // 2) - (alto_ventana // 2) + self.winfo_y()
        ventana.geometry(f"+{x}+{y}")


SCARFApp.start_camera = start_camera
SCARFApp.stop_camera = stop_camera
SCARFApp.on_close = on_close
SCARFApp.actualizar_video = actualizar_video
SCARFApp.guardar_foto = guardar_foto
SCARFApp.cargar_usuarios = cargar_usuarios
SCARFApp.volver_con_cursor = volver_con_cursor

if __name__ == "__main__":
    app = SCARFApp()
    app.mainloop()
  




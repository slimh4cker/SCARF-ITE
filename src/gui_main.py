import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from registro.registrar import registrar_usuario


#ESTA ES LA QUE UTILIZA LA CAMARA DE LA COMPUTADORA (PARA PRUEBAS)
from reconocimiento.reconocimiento import reconocer

#ESTA ES LA QUE SE USA PARA LA CAMARA DE ANDRES
#from reconocimiento.rec import reconocer

# --- Colores base ---
COLOR_AZUL = "#6DA9E4"
COLOR_BOTON = "#3A6D8C"
COLOR_BOTON_HOVER = "#2E4F6E"
COLOR_FONDO = "#F5F7FA"
COLOR_TEXTO = "#1A1A1A"

# Configuración general de CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def mostrar_menu_principal(panel_der, root):
    """Pantalla principal"""
    # Limpiar panel
    for widget in panel_der.winfo_children():
        widget.destroy()

    titulo = ctk.CTkLabel(
        panel_der,
        text="Registro de Usuario",
        text_color=COLOR_TEXTO,
        font=("Segoe UI", 26, "bold")
    )
    titulo.pack(pady=(60, 40))

    btn_registrar = ctk.CTkButton(
        panel_der,
        text="Registrar Usuario",
        fg_color=COLOR_BOTON,
        hover_color=COLOR_BOTON_HOVER,
        text_color="white",
        font=("Segoe UI", 14, "bold"),
        corner_radius=25,
        width=250,
        height=50,
        command=registrar_usuario
    )
    btn_registrar.pack(pady=12)

    btn_analytics = ctk.CTkButton(
        panel_der,
        text="View Analytics",
        fg_color=COLOR_BOTON,
        hover_color=COLOR_BOTON_HOVER,
        text_color="white",
        font=("Segoe UI", 14, "bold"),
        corner_radius=25,
        width=250,
        height=50,
        command=lambda: mostrar_analytics(panel_der, root)
    )
    btn_analytics.pack(pady=12)

    btn_salir = ctk.CTkButton(
        panel_der,
        text="Salir",
        fg_color="#B44444",
        hover_color="#942E2E",
        text_color="white",
        font=("Segoe UI", 14, "bold"),
        corner_radius=25,
        width=250,
        height=50,
        command=root.destroy
    )
    btn_salir.pack(pady=12)

    footer = ctk.CTkLabel(
        panel_der,
        text="Proyecto SCARF ITE © 2025",
        text_color="#7B7B7B",
        font=("Segoe UI", 9)
    )
    footer.pack(side="bottom", pady=10)


def mostrar_analytics(panel_der, root):
    """Pantalla de Analytics dentro del mismo recuadro"""
    # Limpiar panel
    for widget in panel_der.winfo_children():
        widget.destroy()

    titulo = ctk.CTkLabel(
        panel_der,
        text="📊 Dashboard de Analíticas",
        text_color=COLOR_TEXTO,
        font=("Segoe UI", 26, "bold")
    )
    titulo.pack(pady=(60, 20))

    subtitulo = ctk.CTkLabel(
        panel_der,
        text="Aquí se mostrarán los intentos exitosos, fallidos y otros datos del sistema.",
        text_color="#4A4A4A",
        font=("Segoe UI", 13)
    )
    subtitulo.pack(pady=(0, 40))

    btn_volver = ctk.CTkButton(
        panel_der,
        text="Volver al Menú Principal",
        fg_color=COLOR_BOTON,
        hover_color=COLOR_BOTON_HOVER,
        text_color="white",
        font=("Segoe UI", 14, "bold"),
        corner_radius=25,
        width=250,
        height=50,
        command=lambda: mostrar_menu_principal(panel_der, root)
    )
    btn_volver.pack(pady=20)


def ventana_principal():
    root = ctk.CTk()
    root.title("SCARF ITE - Reconocimiento Facial")
    root.geometry("780x450")
    root.resizable(False, False)
    root.configure(fg_color=COLOR_FONDO)

    # Panel izquierdo decorativo
    panel_izq = ctk.CTkFrame(root, fg_color=COLOR_AZUL, width=270)
    panel_izq.pack(side="left", fill="y")

    logo = ctk.CTkLabel(panel_izq, text="👤🔍", text_color="white", font=("Segoe UI Emoji", 80))
    logo.pack(pady=(80, 20))

    texto_desc = ctk.CTkLabel(
        panel_izq,
        text="Sistema de Control Automático\npor Reconocimiento Facial",
        text_color="white",
        font=("Segoe UI", 12, "bold")
    )
    texto_desc.pack(pady=10)

    # Panel derecho dinámico (aquí cambian las vistas)
    panel_der = ctk.CTkFrame(root, fg_color=COLOR_FONDO)
    panel_der.pack(side="right", fill="both", expand=True)

    # Mostrar primera vista
    mostrar_menu_principal(panel_der, root)

    root.mainloop()


if __name__ == "__main__":
    ventana_principal()
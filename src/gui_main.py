import tkinter as tk
from tkinter import messagebox
from registro.registrar import registrar_usuario

#ESTA ES LA QUE UTILIZA LA CAMARA DE LA COMPUTADORA (PARA PRUEBAS)
from reconocimiento.reconocimiento import reconocer

#ESTA ES LA QUE SE USA PARA LA CAMARA DE ANDRES
#from reconocimiento.rec import reconocer

# --- Colores y estilo ---
COLOR_FONDO_IZQ = "#6DA9E4"   # azul para panel izquierdo
COLOR_FONDO_DER = "#F5F7FA"   # fondo principal claro
COLOR_BOTON = "#6DA9E4"       # azul medio
COLOR_BOTON_HOVER = "#2E4F6E" # azul al pasar el mouse
COLOR_TEXTO = "#1A1A1A"
FUENTE_TITULO = ("Segoe UI", 22, "bold")
FUENTE_BOTON = ("Segoe UI", 11, "bold")

def crear_boton(frame, texto, comando):
    """Crea un botón moderno sin sombra"""
    boton = tk.Button(
        frame,
        text=texto,
        command=comando,
        bg=COLOR_BOTON,
        fg="white",
        activebackground=COLOR_BOTON_HOVER,
        activeforeground="white",
        font=FUENTE_BOTON,
        relief="flat",
        bd=0,
        width=20,
        height=2,
        cursor="hand2"
    )

    def on_enter(e): boton.config(bg=COLOR_BOTON_HOVER)
    def on_leave(e): boton.config(bg=COLOR_BOTON)
    boton.bind("<Enter>", on_enter)
    boton.bind("<Leave>", on_leave)

    boton.pack(pady=10)
    return boton

def ventana_principal():
    root = tk.Tk()
    root.title("SCARF ITE - Reconocimiento Facial")
    root.geometry("720x420")
    root.resizable(False, False)
    root.configure(bg=COLOR_FONDO_DER)

    # --- Panel izquierdo decorativo ---
    panel_izq = tk.Frame(root, bg=COLOR_FONDO_IZQ, width=270)
    panel_izq.pack(side="left", fill="y")

    # Logo 
    logo = tk.Label(
        panel_izq,
        text="👤🔍",
        bg=COLOR_FONDO_IZQ,
        fg="white",
        font=("Segoe UI Emoji", 70)
    )
    logo.pack(pady=(80, 20))

    texto_desc = tk.Label(
        panel_izq,
        text="Sistema de Control Automático\npor Reconocimiento Facial",
        bg=COLOR_FONDO_IZQ,
        fg="white",
        font=("Segoe UI", 11, "bold")
    )
    texto_desc.pack(pady=15)

    # --- Panel derecho (principal) ---
    panel_der = tk.Frame(root, bg=COLOR_FONDO_DER)
    panel_der.pack(side="right", fill="both", expand=True)

    titulo = tk.Label(
        panel_der,
        text="Registro de Usuario",
        bg=COLOR_FONDO_DER,
        fg=COLOR_TEXTO,
        font=FUENTE_TITULO
    )
    titulo.pack(pady=(70, 30))

    frame_botones = tk.Frame(panel_der, bg=COLOR_FONDO_DER)
    frame_botones.pack()

    crear_boton(frame_botones, "Registrar Usuario", registrar_usuario)
    crear_boton(frame_botones, "Salir", root.destroy)

    footer = tk.Label(
        panel_der,
        text="Proyecto SCARF ITE © 2025",
        bg=COLOR_FONDO_DER,
        fg="#7B7B7B",
        font=("Segoe UI", 9)
    )
    footer.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    ventana_principal()

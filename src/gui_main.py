import tkinter as tk
from tkinter import messagebox
from registro.registrar import registrar_usuario
from reconocimiento.rec import reconocer

# --- Colores y estilo ---
COLOR_FONDO = "#1A1A2E"
COLOR_BOTON = "#0F3460"
COLOR_HOVER = "#16213E"
COLOR_TEXTO = "#EDEDED"
FUENTE_TITULO = ("Segoe UI", 20, "bold")
FUENTE_BOTON = ("Segoe UI", 12, "bold")

def crear_boton(frame, texto, comando):
    """Crea un botón estilizado con hover"""
    boton = tk.Button(
        frame, text=texto, command=comando,
        bg=COLOR_BOTON, fg=COLOR_TEXTO,
        activebackground=COLOR_HOVER,
        activeforeground=COLOR_TEXTO,
        font=FUENTE_BOTON, relief="flat",
        bd=0, width=22, height=2, cursor="hand2"
    )

    def on_enter(e): boton.config(bg=COLOR_HOVER)
    def on_leave(e): boton.config(bg=COLOR_BOTON)

    boton.bind("<Enter>", on_enter)
    boton.bind("<Leave>", on_leave)
    boton.pack(pady=10)
    return boton

def ventana_principal():
    root = tk.Tk()
    root.title("SCARF ITE - Reconocimiento Facial")
    root.geometry("500x400")
    root.configure(bg=COLOR_FONDO)
    root.resizable(False, False)

    # --- Título ---
    titulo = tk.Label(
        root, text="Reconocimiento Facial",
        bg=COLOR_FONDO, fg=COLOR_TEXTO,
        font=FUENTE_TITULO
    )
    titulo.pack(pady=30)

    # --- Frame para botones ---
    frame_botones = tk.Frame(root, bg=COLOR_FONDO)
    frame_botones.pack()

    crear_boton(frame_botones, "Registrar Usuario", registrar_usuario)
    crear_boton(frame_botones, "Reconocer Usuario", reconocer)
    crear_boton(frame_botones, "Salir", root.destroy)

    # --- Pie de página ---
    footer = tk.Label(
        root, text="Proyecto SCARF ITE © 2025",
        bg=COLOR_FONDO, fg="#BBBBBB", font=("Segoe UI", 9)
    )
    footer.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    ventana_principal()

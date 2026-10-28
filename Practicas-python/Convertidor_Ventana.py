import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp


def elegir_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        var_carpeta.set(carpeta)


def actualizar_barra(porcentaje):
    # Mueve la barra y muestra el porcentaje en el mensaje
    barra["value"] = porcentaje
    estado.set(f"Descargando... {porcentaje:.0f}%")


def progreso(d):
    # yt-dlp llama a esta función cada vez que avanza la descarga
    # "d" es un diccionario con la información del avance
    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        if total:
            porcentaje = d["downloaded_bytes"] / total * 100
            ventana.after(0, actualizar_barra, porcentaje)
    elif d["status"] == "finished":
        # La descarga terminó, ahora ffmpeg convierte el audio
        ventana.after(0, barra.config, {"value": 100})
        ventana.after(0, estado.set, "Convirtiendo a audio...")


def descargar():
    url = entrada_link.get().strip()
    formato = var_formato.get()
    genero = entrada_genero.get().lower().strip() or "sin_genero"
    carpeta_base = var_carpeta.get()

    if url == "":
        messagebox.showwarning("Falta el link", "Pega un link primero.")
        return

    destino = os.path.join(carpeta_base, genero)
    os.makedirs(destino, exist_ok=True)

    barra["value"] = 0  # Reinicia la barra
    boton.config(state="disabled")
    estado.set("Preparando descarga...")

    threading.Thread(target=trabajo, args=(url, formato, destino), daemon=True).start()


def trabajo(url, formato, destino):
    opciones = {
        "noplaylist": True,
        "quiet": True,
        "format": "bestaudio/best",
        "outtmpl": os.path.join(destino, "%(title)s.%(ext)s"),
        "progress_hooks": [progreso],  # Aquí conectamos la barra
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": formato,
            "preferredquality": "320",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        ventana.after(0, terminar, f"¡Listo! Guardado en: {destino}", True)
    except Exception as e:
        print("Error:", e)
        ventana.after(0, terminar, "Hubo un error. Revisa el link.", False)


def terminar(mensaje, exito):
    estado.set(mensaje)
    boton.config(state="normal")
    if exito:
        entrada_link.delete(0, tk.END)
    else:
        barra["value"] = 0


# ---------- Construcción de la ventana ----------
ventana = tk.Tk()
ventana.title("Convertidor de audio")
ventana.geometry("560x320")
ventana.columnconfigure(1, weight=1)
# ---------- Estilo: colores y tamaño ----------
COLOR_FONDO = "#1e1e2e"   # Fondo de la ventana (oscuro)
COLOR_TEXTO = "#ffffff"   # Texto
COLOR_BARRA = "#00d084"   # Color de la barra y los botones
COLOR_RIEL = "#2a2a3c"    # Fondo de la barra (la parte vacía)

ventana.configure(bg=COLOR_FONDO)
ventana.option_add("*Label.background", COLOR_FONDO)
ventana.option_add("*Label.foreground", COLOR_TEXTO)
ventana.option_add("*Button.background", COLOR_BARRA)
ventana.option_add("*Button.foreground", "#000000")
ventana.option_add("*Button.relief", "flat")

estilo = ttk.Style()
estilo.theme_use("clam")  # Este tema permite cambiar colores de la barra
estilo.configure(
    "Verde.Horizontal.TProgressbar",
    troughcolor=COLOR_RIEL,
    background=COLOR_BARRA,
    bordercolor=COLOR_FONDO,
    lightcolor=COLOR_BARRA,
    darkcolor=COLOR_BARRA,
    thickness=22,          # Grosor de la barra
)
var_carpeta = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Music"))
var_formato = tk.StringVar(value="mp3")
estado = tk.StringVar(value="Pega un link y presiona Descargar")

tk.Label(ventana, text="Link:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
entrada_link = tk.Entry(ventana)
entrada_link.grid(row=0, column=1, columnspan=2, padx=10, sticky="ew")

tk.Label(ventana, text="Formato:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Combobox(ventana, textvariable=var_formato, values=("mp3", "flac"),
             state="readonly", width=8).grid(row=1, column=1, padx=10, sticky="w")

tk.Label(ventana, text="Género:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
entrada_genero = tk.Entry(ventana)
entrada_genero.grid(row=2, column=1, columnspan=2, padx=10, sticky="ew")

tk.Label(ventana, text="Carpeta:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
tk.Entry(ventana, textvariable=var_carpeta, state="readonly").grid(row=3, column=1, padx=10, sticky="ew")
tk.Button(ventana, text="Elegir...", command=elegir_carpeta).grid(row=3, column=2, padx=10)

boton = tk.Button(ventana, text="Descargar", command=descargar)
boton.grid(row=4, column=0, columnspan=3, pady=10)

# La barra de progreso (va de 0 a 100)
barra = ttk.Progressbar(ventana, orient="horizontal", mode="determinate", maximum=100)
barra.grid(row=5, column=0, columnspan=3, padx=20, pady=5, sticky="ew")

tk.Label(ventana, textvariable=estado, wraplength=520).grid(row=6, column=0, columnspan=3, padx=10, pady=5)

ventana.mainloop()
import os
import yt_dlp

# Carpeta principal donde se guardará toda la música
carpeta_base = input("Carpeta principal (Enter para usar 'Musica'): ").strip()
if carpeta_base == "":
    carpeta_base = "Musica"

# El programa se repite hasta que escribas 'salir'
while True:
    url = input("\nPega el link (o escribe 'salir'): ").strip()
    if url.lower() == "salir":
        print("¡Hasta luego!")
        break

    formato = input("Formato (mp3/flac): ").lower().strip()
    if formato not in ("mp3", "flac"):
        print("Formato no válido. Usa mp3 o flac.")
        continue  # Vuelve a pedir otro link

    genero = input("Género (ej. house, techno, trance): ").lower().strip()
    if genero == "":
        genero = "sin_genero"

    # Creamos la carpeta del género si no existe: Musica/house
    destino = os.path.join(carpeta_base, genero)
    os.makedirs(destino, exist_ok=True)

    opciones = {
        "noplaylist": True,
        "format": "bestaudio/best",
        "outtmpl": os.path.join(destino, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": formato,
            "preferredquality": "320",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        print(f"¡Listo! Guardado en: {destino}")
    except Exception as e:
        print("Hubo un error:", e)
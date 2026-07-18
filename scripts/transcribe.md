# transcribe.py

Transcribe videos/audio a `.txt` en español usando [faster-whisper](https://github.com/SYSTRAN/faster-whisper), corriendo 100% local en CPU (sin GPU, sin subir nada a internet).

Pensado originalmente para transcribir clases grabadas (`Videos/Alice`), pero el script no tiene ninguna ruta hardcodeada: sirve para cualquier carpeta de videos/audios.

## Setup (una sola vez por máquina o por proyecto)

Requiere `ffmpeg` instalado en el sistema y Python 3.

```bash
# 1. crear un entorno virtual (Debian/Ubuntu bloquea pip install global)
python3 -m venv .venv-whisper
.venv-whisper/bin/pip install --upgrade pip
.venv-whisper/bin/pip install faster-whisper

# 2. ffmpeg, si no lo tenés
sudo apt install ffmpeg
```

El entorno `.venv-whisper` se puede crear donde sea más cómodo (al lado del script, o en la raíz del proyecto de videos); el script no depende de dónde esté ese venv, solo hay que invocarlo con ese intérprete.

## Uso

```bash
# un archivo
.venv-whisper/bin/python scripts/transcribe.py "carpeta/clase 1.mp4"

# varios archivos
.venv-whisper/bin/python scripts/transcribe.py "clase 1.mp4" "clase 2.mp4"

# una carpeta entera (recorre subcarpetas recursivamente)
.venv-whisper/bin/python scripts/transcribe.py --folder "/ruta/al/curso"

# modelo más preciso pero más lento (default: small)
.venv-whisper/bin/python scripts/transcribe.py --folder "/ruta" --model medium

# otro idioma (default: es)
.venv-whisper/bin/python scripts/transcribe.py --folder "/ruta" --lang en
```

Formatos de entrada aceptados automáticamente: `.mp4 .mov .mkv .webm .m4a .mp3 .wav` (no hace falta que sea mp4 específicamente).

## Output

Por cada `algo.mp4` genera `algo.txt` al lado del video (recortando un espacio final en el nombre si lo tiene, ej. `"Clase 2 .mp4"` → `"Clase 2.txt"`), con este formato de segmentos:

```
[00:00:03 --> 00:00:10] texto del segmento transcripto
[00:00:10 --> 00:00:17] siguiente segmento...
```

Si el `.txt` ya existe, el archivo se salta (así se puede volver a correr sobre una carpeta para completar solo lo que falta).

## Modelo: `small` vs `medium`

- `small` (default): en una laptop sin GPU corre en general a ~8-9x tiempo real. Calidad buena para uso normal.
- `medium`: bastante más preciso, pero ronda ~2.4x tiempo real (varias veces más lento). Usar solo si la precisión importa más que el tiempo.

En una corrida de referencia (CPU i7-10510U, 8 hilos, sin GPU) sobre ~5.5 horas de audio en total: `small` tardó ~45 minutos, `medium` hubiera tardado varias horas.

## Correrlo en segundo plano

Para carpetas grandes, conviene lanzarlo en background y no esperarlo bloqueando la terminal:

```bash
nohup .venv-whisper/bin/python scripts/transcribe.py --folder "/ruta/al/curso" > transcribe.log 2>&1 &
tail -f transcribe.log
```

El script imprime una línea por archivo (`START:`, `DONE:` con segundos y cantidad de segmentos, o `SKIP (exists):`) y termina con `ALL_DONE`.

## Resúmenes (`Resumen.md`)

Este script solo genera la transcripción cruda. Si además querés un resumen en markdown por clase (frontmatter `fecha`/`modulo`/`tema` + secciones temáticas + preguntas y respuestas + conclusión, formato usado en el proyecto Alice), pedilo aparte una vez que tengas los `.txt` — no lo genera automáticamente este script.

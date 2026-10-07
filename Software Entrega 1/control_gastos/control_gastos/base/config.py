"""Configuración y constantes compartidas por toda la app."""
from pathlib import Path

# Conexión a la base de datos SQLite (archivo gastos.db).
DB_URL = "sqlite:///gastos.db"

# Ruta del archivo de documentación HTML (vive junto a este archivo).
RUTA_DOCUMENTACION = Path(__file__).parent.parent / "documentacion.html"

# UI: nombres de los meses en español para mostrarlos en pantalla.
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

# UI: emoji de cada categoría (solo se ve en el selector, no cambia lo guardado).
ICONOS_CATEGORIA = {
    "Comida": "🍽️",
    "Transporte": "🚌",
    "Ocio": "🎟️",
    "Otros": "📦",
}

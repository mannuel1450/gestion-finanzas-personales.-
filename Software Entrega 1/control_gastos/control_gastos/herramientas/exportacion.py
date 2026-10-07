"""Exportación de datos a archivos."""
from pathlib import Path

from logica.gastos_service import obtener_dataframe


# LÓGICA: guarda todos los gastos en un archivo CSV (abre en Excel).
def exportar_gastos_csv(usuario_id: int) -> Path:
   
    df = obtener_dataframe(usuario_id)

    # Crea la carpeta 'exportaciones' si no existe.
    carpeta = Path("exportaciones")
    carpeta.mkdir(parents=True, exist_ok=True)

    archivo = carpeta / f"gastos_usuario_{usuario_id}.csv"


    # Orden de las columnas del archivo.
    columnas = ["ID", "Fecha", "Concepto", "Categoría", "Monto"]
    df_exportar = df[columnas].copy()

    # Escribe el CSV (utf-8-sig para que Excel muestre bien los acentos).
    df_exportar.to_csv(
        archivo,
        index=False,
        encoding="utf-8-sig"
    )

    return archivo

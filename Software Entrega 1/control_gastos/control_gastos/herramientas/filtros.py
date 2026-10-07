"""Filtros y métricas sobre la tabla de gastos (pandas)."""
from datetime import date

import pandas as pd


# LÓGICA: filtra la tabla por categoría y rango de fechas.
def aplicar_filtros(
    df: pd.DataFrame,
    categoria: str,
    fecha_min: date,
    fecha_max: date
) -> pd.DataFrame:
    if df.empty:
        return df

    fecha_min = pd.to_datetime(fecha_min)
    fecha_max = pd.to_datetime(fecha_max)

    # Si eligió una categoría, deja solo esas filas.
    if categoria != "Todas":
        df = df[df["Categoría"] == categoria]

    df = df[
        (df["Fecha"] >= fecha_min) &
        (df["Fecha"] <= fecha_max)
    ]

    return df


# LÓGICA: suma la columna Monto (0 si la tabla está vacía).
def calcular_total(df: pd.DataFrame) -> float:
    return df["Monto"].sum() if not df.empty else 0.0

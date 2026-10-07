"""Lógica de gastos: agregar, consultar y eliminar."""
from datetime import date

import pandas as pd
from sqlmodel import Session, select

from base.database import engine
from base.models import Gasto


# LÓGICA: valida y guarda un gasto nuevo.
def agregar_gasto(
    concepto: str,
    monto: float,
    categoria: str,
    fecha: date,
    usuario_id: int
) -> tuple[bool, str]:
    """Valida y guarda un gasto."""
    # Validaciones: concepto lleno (máx. 50), monto > 0 y fecha no futura.
    if not concepto or not concepto.strip():
        return False, "El concepto no puede estar vacío."

    if len(concepto.strip()) > 50:
        return False, "El concepto no puede tener más de 50 caracteres."

    if monto <= 0:
        return False, "El monto debe ser mayor a cero."

    if fecha > date.today():
        return False, "La fecha no puede ser futura."

    # Si todo está bien, guarda el gasto en la base de datos.
    with Session(engine) as session:
        gasto = Gasto(
            concepto=concepto.strip(),
            monto=monto,
            categoria=categoria,
            fecha=fecha,
            usuario_id=usuario_id
        )

        session.add(gasto)
        session.commit()

    return True, "¡Gasto registrado!"


# LÓGICA: trae los gastos del usuario (más recientes primero) en forma de tabla.
def obtener_dataframe(usuario_id: int) -> pd.DataFrame:
    """Devuelve DataFrame con los gastos del usuario."""
    with Session(engine) as session:
        # Consulta a la base de datos: solo los gastos de este usuario.
        gastos = session.exec(
            select(Gasto)
            .where(Gasto.usuario_id == usuario_id)
            .order_by(Gasto.fecha.desc(), Gasto.id.desc())
        ).all()

    # Si no hay gastos, devuelve una tabla vacía con las columnas.
    if not gastos:
        return pd.DataFrame(
            columns=[
                "ID",
                "Concepto",
                "Monto",
                "Categoría",
                "Fecha"
            ]
        )

    # Convierte cada gasto en una fila de la tabla.
    df = pd.DataFrame([
        {
            "ID": g.id,
            "Concepto": g.concepto,
            "Monto": g.monto,
            "Categoría": g.categoria,
            "Fecha": g.fecha
        }
        for g in gastos
    ])

    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df


# LÓGICA: borra un gasto, solo si pertenece al usuario.
def eliminar_gasto(
    gasto_id: int,
    usuario_id: int
) -> tuple[bool, str]:
    
    with Session(engine) as session:
        # Busca el gasto por su ID.
        gasto = session.get(Gasto, gasto_id)

        if not gasto:
            return False, "El gasto no existe."

        # Seguridad: nadie puede borrar gastos de otro usuario.
        if gasto.usuario_id != usuario_id:
            return False, "No tienes permiso para eliminar este gasto."

        session.delete(gasto)
        session.commit()

    return True, "Gasto eliminado correctamente."

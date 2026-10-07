"""Lógica de presupuesto mensual: guardar, consultar y alertar."""
from datetime import date
from typing import Optional

from sqlmodel import Session, select

from base.database import engine
from base.models import Gasto, Presupuesto


# LÓGICA: guarda (o actualiza) el presupuesto de un mes.
def guardar_presupuesto(
    usuario_id: int,
    anio: int,
    mes: int,
    monto: float
) -> tuple[bool, str]:

    # Validaciones: monto mayor a 0 y mes entre 1 y 12.
    if monto <= 0:
        return False, "El presupuesto debe ser mayor a cero."

    if mes < 1 or mes > 12:
        return False, "El mes no es válido."

    with Session(engine) as session:
        # Busca si ya existe un presupuesto para ese mes.
        presupuesto = session.exec(
            select(Presupuesto).where(
                Presupuesto.usuario_id == usuario_id,
                Presupuesto.anio == anio,
                Presupuesto.mes == mes
            )
        ).first()

        # Si existe lo actualiza; si no, crea uno nuevo.
        if presupuesto:
            presupuesto.monto = monto
        else:
            presupuesto = Presupuesto(
                usuario_id=usuario_id,
                anio=anio,
                mes=mes,
                monto=monto
            )
            session.add(presupuesto)

        session.commit()

    return True, "Presupuesto guardado correctamente."


# LÓGICA: devuelve el presupuesto de un mes (o None si no hay).
def obtener_presupuesto(
    usuario_id: int,
    anio: int,
    mes: int
) -> Optional[float]:
    """Obtiene el presupuesto del mes indicado."""
    with Session(engine) as session:
        presupuesto = session.exec(
            select(Presupuesto).where(
                Presupuesto.usuario_id == usuario_id,
                Presupuesto.anio == anio,
                Presupuesto.mes == mes
            )
        ).first()

        if presupuesto:
            return presupuesto.monto

    return None


# LÓGICA: suma todo lo gastado en un mes.
def calcular_gasto_mensual(
    usuario_id: int,
    anio: int,
    mes: int
) -> float:
    
    # Rango del mes: desde el día 1 hasta el día 1 del mes siguiente.
    inicio = date(anio, mes, 1)

    if mes == 12:
        siguiente_mes = date(anio + 1, 1, 1)
    else:
        siguiente_mes = date(anio, mes + 1, 1)

    with Session(engine) as session:
        # Trae los gastos del usuario dentro de ese rango.
        gastos = session.exec(
            select(Gasto).where(
                Gasto.usuario_id == usuario_id,
                Gasto.fecha >= inicio,
                Gasto.fecha < siguiente_mes
            )
        ).all()

        return sum(g.monto for g in gastos)


# LÓGICA: dice si ya se alcanzó o pasó el presupuesto del mes.
def verificar_alerta_presupuesto(
    usuario_id: int,
    anio: int,
    mes: int
) -> tuple[bool, float, Optional[float]]:
   
    presupuesto = obtener_presupuesto(usuario_id, anio, mes)

    if presupuesto is None:
        return False, 0.0, None

    acumulado = calcular_gasto_mensual(
        usuario_id,
        anio,
        mes
    )

    # Hay alerta cuando lo gastado iguala o supera el presupuesto.
    alerta = acumulado >= presupuesto

    return alerta, acumulado, presupuesto

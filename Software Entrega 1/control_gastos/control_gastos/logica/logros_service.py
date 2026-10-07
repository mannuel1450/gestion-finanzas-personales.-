"""Lógica de logros: definición, desbloqueo y consulta."""
from datetime import timedelta

from sqlmodel import Session, select

from base.database import engine
from base.models import Gasto, Logro, TipoLogro


# LÓGICA: lista de logros: (tipo, nombre, descripción que ve el usuario).
DEFINICION_LOGROS = [
    (
        TipoLogro.PRIMER_GASTO,
        "Primer gasto",
        "Registraste tu primer gasto 🎉"
    ),
    (
        TipoLogro.CINCO_GASTOS,
        "5 gastos",
        "Registraste 5 gastos 📊"
    ),
    (
        TipoLogro.AHORRO_BAJO,
        "Ahorro bajo",
        "Gastaste menos de $100 en total 💪"
    ),


    # registrar gastos durante 3 días seguidos.
    (
        TipoLogro.TRES_DIAS_SEGUIDOS,
        "3 días seguidos",
        "Registraste gastos durante 3 días seguidos 🔥"
    ),

    # Segundo logro sencillo relacionado con el uso de la aplicación.
    (
        TipoLogro.DIEZ_GASTOS,
        "10 gastos",
        "Registraste 10 gastos en la aplicación 🚀"
    ),
]


# LÓGICA: crea en la base de datos los logros que le falten al usuario.
def inicializar_logros(usuario_id: int) -> None:
    """
    Crea los logros que todavía no existan para el usuario.
    Esto permite agregar nuevos logros sin perder los anteriores.
    """
    with Session(engine) as session:
        # Logros que el usuario ya tiene.
        existentes = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        tipos_existentes = {logro.tipo for logro in existentes}

        # Agrega solo los que faltan (así no se pierden los anteriores).
        for tipo, nombre, desc in DEFINICION_LOGROS:
            if tipo not in tipos_existentes:
                session.add(
                    Logro(
                        tipo=tipo,
                        nombre=nombre,
                        descripcion=desc,
                        usuario_id=usuario_id
                    )
                )

        session.commit()


# LÓGICA: revisa si hay gastos registrados en 3 días consecutivos.
def tiene_tres_dias_seguidos(gastos: list[Gasto]) -> bool:
    
    if not gastos:
        return False

    # Días únicos con gastos, ordenados de antiguo a reciente.
    dias = sorted({g.fecha for g in gastos})

    if len(dias) < 3:
        return False

    consecutivos = 1

    # Cuenta días seguidos; si se rompe la racha, vuelve a empezar.
    for i in range(1, len(dias)):
        if dias[i] == dias[i - 1] + timedelta(days=1):
            consecutivos += 1

            if consecutivos >= 3:
                return True
        else:
            consecutivos = 1

    return False


# LÓGICA: revisa qué logros se cumplen y devuelve los recién desbloqueados.
def verificar_logros(usuario_id: int) -> list[str]:
    """
    Verifica los logros del usuario y devuelve los nombres de los
    logros que se desbloquearon en esta comprobación.
    """
    nuevos_desbloqueos = []

    with Session(engine) as session:
        gastos = session.exec(
            select(Gasto).where(Gasto.usuario_id == usuario_id)
        ).all()

        # Datos que se usan para evaluar los logros.
        total = sum(g.monto for g in gastos)
        dias_seguidos = tiene_tres_dias_seguidos(gastos)

        logros = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        # Condición de cada logro: 1 gasto, 5 gastos, total menor a $100, 3 días seguidos, 10 gastos.
        cumple = {
            TipoLogro.PRIMER_GASTO: len(gastos) >= 1,
            TipoLogro.CINCO_GASTOS: len(gastos) >= 5,
            TipoLogro.AHORRO_BAJO: 0 < total < 100,
            TipoLogro.TRES_DIAS_SEGUIDOS: dias_seguidos,
            TipoLogro.DIEZ_GASTOS: len(gastos) >= 10,
        }

        # Un logro, una vez desbloqueado, ya no se vuelve a bloquear.
        for logro in logros:
            if not logro.desbloqueado and cumple.get(logro.tipo, False):
                logro.desbloqueado = True
                session.add(logro)
                nuevos_desbloqueos.append(logro.nombre)

        session.commit()

    return nuevos_desbloqueos


# LÓGICA: devuelve los logros del usuario para mostrarlos.
def obtener_logros(usuario_id: int) -> list[Logro]:
    """Obtiene los logros del usuario."""
    with Session(engine) as session:
        logros = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        return [
            Logro(
                id=l.id,
                tipo=l.tipo,
                nombre=l.nombre,
                descripcion=l.descripcion,
                desbloqueado=l.desbloqueado,
                usuario_id=l.usuario_id
            )
            for l in logros
        ]

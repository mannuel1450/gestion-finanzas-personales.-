import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
from enum import Enum
import bcrypt

from sqlmodel import SQLModel, Field, create_engine, Session, select


# =========================
#  MODELOS
# =========================

class TipoLogro(str, Enum):
    PRIMER_GASTO = "primer_gasto"
    CINCO_GASTOS = "cinco_gastos"
    AHORRO_BAJO = "ahorro_bajo"


    TRES_DIAS_SEGUIDOS = "tres_dias_seguidos"
    DIEZ_GASTOS = "diez_gastos"


class Usuario(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class Gasto(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    concepto: str
    monto: float
    categoria: str
    fecha: date
    usuario_id: int = Field(foreign_key="usuario.id")


class Presupuesto(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    anio: int
    mes: int
    monto: float


class Logro(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: TipoLogro
    nombre: str
    descripcion: str
    desbloqueado: bool = False
    usuario_id: int = Field(foreign_key="usuario.id")


engine = create_engine("sqlite:///gastos.db", echo=False)


def crear_db():
    SQLModel.metadata.create_all(engine)


# =========================
# SEGURIDAD
# =========================

def hash_password(password: str) -> str:
    """Genera hash bcrypt con salt automático."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, hashed: str) -> bool:
    """Verifica contraseña contra hash bcrypt."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# =========================
# USUARIOS
# =========================

def registrar_usuario(username: str, password: str) -> tuple[bool, str]:
    """Registra usuario. Retorna (éxito, mensaje)."""
    if not username or len(username.strip()) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if not password or len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    with Session(engine) as session:
        existente = session.exec(
            select(Usuario).where(Usuario.username == username.strip())
        ).first()

        if existente:
            return False, "Ese nombre de usuario ya está registrado."

        nuevo = Usuario(
            username=username.strip(),
            password=hash_password(password)
        )
        session.add(nuevo)
        session.commit()

        return True, "Usuario creado correctamente."


def login_usuario(username: str, password: str) -> Optional[Usuario]:
    """Retorna el objeto Usuario si las credenciales son válidas."""
    with Session(engine) as session:
        user = session.exec(
            select(Usuario).where(Usuario.username == username.strip())
        ).first()

        if user and verificar_password(password, user.password):
            session.refresh(user)
            return Usuario(
                id=user.id,
                username=user.username,
                password=user.password
            )

        return None


# =========================
# GASTOS
# =========================

def agregar_gasto(
    concepto: str,
    monto: float,
    categoria: str,
    fecha: date,
    usuario_id: int
) -> tuple[bool, str]:
    """Valida y guarda un gasto."""
    if not concepto or not concepto.strip():
        return False, "El concepto no puede estar vacío."

    if len(concepto.strip()) > 50:
        return False, "El concepto no puede tener más de 50 caracteres."

    if monto <= 0:
        return False, "El monto debe ser mayor a cero."

    if fecha > date.today():
        return False, "La fecha no puede ser futura."

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


def obtener_dataframe(usuario_id: int) -> pd.DataFrame:
    """Devuelve DataFrame con los gastos del usuario."""
    with Session(engine) as session:
        gastos = session.exec(
            select(Gasto)
            .where(Gasto.usuario_id == usuario_id)
            .order_by(Gasto.fecha.desc(), Gasto.id.desc())
        ).all()

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


def eliminar_gasto(
    gasto_id: int,
    usuario_id: int
) -> tuple[bool, str]:
    
    with Session(engine) as session:
        gasto = session.get(Gasto, gasto_id)

        if not gasto:
            return False, "El gasto no existe."

        if gasto.usuario_id != usuario_id:
            return False, "No tienes permiso para eliminar este gasto."

        session.delete(gasto)
        session.commit()

    return True, "Gasto eliminado correctamente."


# =========================
# PRESUPUESTO
# =========================

def guardar_presupuesto(
    usuario_id: int,
    anio: int,
    mes: int,
    monto: float
) -> tuple[bool, str]:

    if monto <= 0:
        return False, "El presupuesto debe ser mayor a cero."

    if mes < 1 or mes > 12:
        return False, "El mes no es válido."

    with Session(engine) as session:
        presupuesto = session.exec(
            select(Presupuesto).where(
                Presupuesto.usuario_id == usuario_id,
                Presupuesto.anio == anio,
                Presupuesto.mes == mes
            )
        ).first()

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


def calcular_gasto_mensual(
    usuario_id: int,
    anio: int,
    mes: int
) -> float:
    
    inicio = date(anio, mes, 1)

    if mes == 12:
        siguiente_mes = date(anio + 1, 1, 1)
    else:
        siguiente_mes = date(anio, mes + 1, 1)

    with Session(engine) as session:
        gastos = session.exec(
            select(Gasto).where(
                Gasto.usuario_id == usuario_id,
                Gasto.fecha >= inicio,
                Gasto.fecha < siguiente_mes
            )
        ).all()

        return sum(g.monto for g in gastos)


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

    alerta = acumulado >= presupuesto

    return alerta, acumulado, presupuesto


# =========================
# EXPORTACIÓN CSV
# =========================

def exportar_gastos_csv(usuario_id: int) -> Path:
   
    df = obtener_dataframe(usuario_id)

    carpeta = Path("exportaciones")
    carpeta.mkdir(parents=True, exist_ok=True)

    archivo = carpeta / f"gastos_usuario_{usuario_id}.csv"


    columnas = ["ID", "Fecha", "Concepto", "Categoría", "Monto"]
    df_exportar = df[columnas].copy()

    df_exportar.to_csv(
        archivo,
        index=False,
        encoding="utf-8-sig"
    )

    return archivo



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


def inicializar_logros(usuario_id: int) -> None:
    """
    Crea los logros que todavía no existan para el usuario.
    Esto permite agregar nuevos logros sin perder los anteriores.
    """
    with Session(engine) as session:
        existentes = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        tipos_existentes = {logro.tipo for logro in existentes}

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


def tiene_tres_dias_seguidos(gastos: list[Gasto]) -> bool:
    
    if not gastos:
        return False

    dias = sorted({g.fecha for g in gastos})

    if len(dias) < 3:
        return False

    consecutivos = 1

    for i in range(1, len(dias)):
        if dias[i] == dias[i - 1] + timedelta(days=1):
            consecutivos += 1

            if consecutivos >= 3:
                return True
        else:
            consecutivos = 1

    return False


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

        total = sum(g.monto for g in gastos)
        dias_seguidos = tiene_tres_dias_seguidos(gastos)

        logros = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        for logro in logros:
            estaba_desbloqueado = logro.desbloqueado

            if logro.tipo == TipoLogro.PRIMER_GASTO:
                logro.desbloqueado = len(gastos) >= 1

            elif logro.tipo == TipoLogro.CINCO_GASTOS:
                logro.desbloqueado = len(gastos) >= 5

            elif logro.tipo == TipoLogro.AHORRO_BAJO:
                logro.desbloqueado = 0 < total < 100

            elif logro.tipo == TipoLogro.TRES_DIAS_SEGUIDOS:
                logro.desbloqueado = dias_seguidos

            elif logro.tipo == TipoLogro.DIEZ_GASTOS:
                logro.desbloqueado = len(gastos) >= 10

            if logro.desbloqueado and not estaba_desbloqueado:
                nuevos_desbloqueos.append(logro.nombre)

        session.commit()

    return nuevos_desbloqueos


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


# =========================
# FILTROS Y MÉTRICAS
# =========================

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

    if categoria != "Todas":
        df = df[df["Categoría"] == categoria]

    df = df[
        (df["Fecha"] >= fecha_min) &
        (df["Fecha"] <= fecha_max)
    ]

    return df


def calcular_total(df: pd.DataFrame) -> float:
    return df["Monto"].sum() if not df.empty else 0.0


# =========================
# LOGIN UI
# =========================

def inicializar_auth() -> None:
    if "usuario" not in st.session_state:
        st.session_state.usuario = None


def pantalla_login() -> None:
    st.title("Control de Gastos — Acceso")

    opcion = st.radio(
        "",
        ["Iniciar sesión", "Crear cuenta"],
        horizontal=True
    )

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if opcion == "Crear cuenta":
        if st.button("Registrarse", use_container_width=True):
            ok, msg = registrar_usuario(username, password)
            (st.success if ok else st.error)(msg)

    else:
        if st.button("Entrar", use_container_width=True):
            user = login_usuario(username, password)

            if user:
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")


# =========================
# APP PRINCIPAL
# =========================

def main() -> None:
    st.set_page_config(
        page_title="Control de Gastos Pro",
        layout="wide"
    )

    crear_db()
    inicializar_auth()

    if st.session_state.usuario is None:
        pantalla_login()
        return

    usuario = st.session_state.usuario

    
    inicializar_logros(usuario.id)
    nuevos_logros = verificar_logros(usuario.id)

    # Aviso visible cuando se desbloquea un logro.
    for nombre_logro in nuevos_logros:
        st.success(f"🏆 ¡Logro desbloqueado!: {nombre_logro}")

    # ── Sidebar ──────────────────────────────────────────────
    st.sidebar.title("Mis Finanzas")
    st.sidebar.write(f"**{usuario.username}**")

    if st.sidebar.button(
        "Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.usuario = None
        st.rerun()

    st.title("Control de Gastos")

    # ── Formulario de gasto ─────────────────────────────────
    st.subheader("Agregar gasto")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        concepto = st.text_input("Concepto")

    with col2:
        monto = st.number_input(
            "Monto",
            min_value=0.0,
            step=10.0
        )

    with col3:
        categoria = st.selectbox(
            "Categoría",
            ["Comida", "Transporte", "Ocio", "Otros"]
        )

    with col4:
        fecha = st.date_input(
            "Fecha",
            value=date.today()
        )

    if st.button("Agregar", use_container_width=False):
        ok, msg = agregar_gasto(
            concepto,
            monto,
            categoria,
            fecha,
            usuario.id
        )

        (st.success if ok else st.warning)(msg)

        if ok:
            st.rerun()

    df = obtener_dataframe(usuario.id)

    st.divider()

    
    st.subheader("Eliminar gasto")

    if not df.empty:
        opciones = {
            f"#{int(row['ID'])} — {row['Concepto']} — "
            f"${float(row['Monto']):,.2f}": int(row["ID"])
            for _, row in df.iterrows()
        }

        gasto_seleccionado = st.selectbox(
            "Selecciona el gasto que deseas eliminar",
            list(opciones.keys())
        )

        confirmar = st.checkbox(
            "Confirmo que deseo eliminar este gasto."
        )

        if st.button("Eliminar gasto"):
            if not confirmar:
                st.warning(
                    "Debes confirmar la eliminación antes de continuar."
                )
            else:
                gasto_id = opciones[gasto_seleccionado]

                ok, msg = eliminar_gasto(
                    gasto_id,
                    usuario.id
                )

                (st.success if ok else st.error)(msg)

                if ok:
                    st.rerun()
    else:
        st.info("No hay gastos para eliminar.")

    
    st.divider()
    st.subheader("Presupuesto mensual")

    hoy = date.today()
    presupuesto_actual = obtener_presupuesto(
        usuario.id,
        hoy.year,
        hoy.month
    )

    if presupuesto_actual is not None:
        st.info(
            f"Presupuesto de {hoy.strftime('%B de %Y')}: "
            f"${presupuesto_actual:,.2f}"
        )

    presupuesto_input = st.number_input(
        "Define tu presupuesto para el mes actual",
        min_value=0.0,
        step=100.0,
        value=float(presupuesto_actual or 0.0)
    )

    if st.button("Guardar presupuesto"):
        ok, msg = guardar_presupuesto(
            usuario.id,
            hoy.year,
            hoy.month,
            presupuesto_input
        )

        (st.success if ok else st.warning)(msg)

        if ok:
            st.rerun()

    
    alerta, acumulado, presupuesto = verificar_alerta_presupuesto(
        usuario.id,
        hoy.year,
        hoy.month
    )

    if presupuesto is not None:
        if alerta:
            st.error(
                f"🚨 ALERTA DE PRESUPUESTO: has gastado "
                f"${acumulado:,.2f} de ${presupuesto:,.2f}."
            )
        else:
            restante = presupuesto - acumulado
            st.info(
                f"Presupuesto: ${presupuesto:,.2f} | "
                f"Acumulado: ${acumulado:,.2f} | "
                f"Disponible: ${restante:,.2f}"
            )

    
    st.divider()
    st.subheader("Exportar gastos")

    if st.button("Generar archivo CSV"):
        with st.spinner("Generando archivo..."):
            archivo_csv = exportar_gastos_csv(usuario.id)
            datos_csv = archivo_csv.read_bytes()

        st.download_button(
            label="Descargar CSV",
            data=datos_csv,
            file_name=archivo_csv.name,
            mime="text/csv"
        )

    # ── Filtros ──────────────────────────────────────────────
    st.divider()
    st.subheader("Filtros")

    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        cat_filtro = st.selectbox(
            "Filtrar por categoría",
            ["Todas", "Comida", "Transporte", "Ocio", "Otros"]
        )

    with colf2:
        fecha_min = st.date_input(
            "Desde",
            value=date(2024, 1, 1)
        )

    with colf3:
        fecha_max = st.date_input(
            "Hasta",
            value=date.today()
        )

    df_filtrado = aplicar_filtros(
        df,
        cat_filtro,
        fecha_min,
        fecha_max
    )

    # ── Tabla ────────────────────────────────────────────────
    st.subheader("Datos")

    if not df_filtrado.empty:
        cols_mostrar = [
            "ID",
            "Concepto",
            "Monto",
            "Categoría",
            "Fecha"
        ]

        cols_existentes = [
            c for c in cols_mostrar
            if c in df_filtrado.columns
        ]

        st.dataframe(
            df_filtrado[cols_existentes],
            use_container_width=True
        )
    else:
        st.info("No hay gastos que coincidan con los filtros.")

    # ── Métricas ────────────────────────────────────────────
    total = calcular_total(df_filtrado)

    mc1, mc2, mc3 = st.columns(3)

    mc1.metric(
        "Total gastado",
        f"${total:,.2f}"
    )

    mc2.metric(
        "Número de gastos",
        len(df_filtrado)
    )

    if not df_filtrado.empty:
        mc3.metric(
            "Promedio por gasto",
            f"${total / len(df_filtrado):,.2f}"
        )

    # ── Gráficas ────────────────────────────────────────────
    st.subheader("Visualización")

    if not df_filtrado.empty:
        colg1, colg2 = st.columns(2)

        with colg1:
            st.write("**Gasto por categoría**")
            st.bar_chart(
                df_filtrado.groupby("Categoría")["Monto"].sum()
            )

        with colg2:
            st.write("**Gasto por fecha**")
            st.line_chart(
                df_filtrado.groupby("Fecha")["Monto"].sum()
            )
    else:
        st.info("No hay datos para graficar.")

    # ── Logros ───────────────────────────────────────────────
    st.subheader("Logros")

    logros = obtener_logros(usuario.id)

    cols = st.columns(len(logros)) if logros else []

    for i, logro in enumerate(logros):
        with cols[i]:
            if logro.desbloqueado:
                st.success(
                    f"**{logro.nombre}**\n\n"
                    f"{logro.descripcion}"
                )
            else:
                st.warning(
                    f"**{logro.nombre}**\n\n"
                    f"{logro.descripcion}"
                )


if __name__ == "__main__":
    main()

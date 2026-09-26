from datetime import date
from enum import Enum
from typing import Optional

import bcrypt
import pandas as pd
import streamlit as st
from sqlmodel import Field, Session, SQLModel, create_engine, select

# =========================
# MODELOS
# =========================


class TipoLogro(str, Enum):
    PRIMER_GASTO = "primer_gasto"
    CINCO_GASTOS = "cinco_gastos"
    AHORRO_BAJO = "ahorro_bajo"


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
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# =========================
# USUARIOS
# =========================


def registrar_usuario(username: str, password: str) -> tuple[bool, str]:
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
            username=username.strip(), password=hash_password(password)
        )
        session.add(nuevo)
        session.commit()
        return True, "Usuario creado correctamente."


def login_usuario(username: str, password: str) -> Optional[Usuario]:
    with Session(engine) as session:
        user = session.exec(
            select(Usuario).where(Usuario.username == username.strip())
        ).first()
        if user and verificar_password(password, user.password):
            return Usuario(
                id=user.id, username=user.username, password=user.password
            )
        return None


# =========================
# GASTOS
# =========================


def agregar_gasto(
    concepto: str, monto: float, categoria: str, fecha: date, usuario_id: int
) -> tuple[bool, str]:
    if not concepto or not concepto.strip():
        return False, "El concepto no puede estar vacío."
    if monto <= 0:
        return False, "El monto debe ser mayor a cero."

    with Session(engine) as session:
        gasto = Gasto(
            concepto=concepto.strip(),
            monto=monto,
            categoria=categoria,
            fecha=fecha,
            usuario_id=usuario_id,
        )
        session.add(gasto)
        session.commit()
    return True, "¡Gasto registrado!"


def obtener_dataframe(usuario_id: int) -> pd.DataFrame:
    with Session(engine) as session:
        gastos = session.exec(
            select(Gasto).where(Gasto.usuario_id == usuario_id)
        ).all()

    if not gastos:
        return pd.DataFrame()

    df = pd.DataFrame([g.model_dump() for g in gastos])
    df.rename(
        columns={
            "concepto": "Concepto",
            "monto": "Monto",
            "categoria": "Categoría",
            "fecha": "Fecha",
        },
        inplace=True,
    )
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df


def eliminar_gasto(gasto_id: int) -> None:
    with Session(engine) as session:
        gasto = session.get(Gasto, gasto_id)
        if gasto:
            session.delete(gasto)
            session.commit()


# =========================
# GAMIFICACIÓN
# =========================

DEFINICION_LOGROS = [
    (TipoLogro.PRIMER_GASTO, "Primer gasto", "Registraste tu primer gasto 🎉"),
    (TipoLogro.CINCO_GASTOS, "5 gastos", "Registraste 5 gastos 📊"),
    (
        TipoLogro.AHORRO_BAJO,
        "Ahorro bajo",
        "Gastaste menos de $100 en total 💪",
    ),
]


def inicializar_logros(usuario_id: int) -> None:
    with Session(engine) as session:
        existentes = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()
        if not existentes:
            for tipo, nombre, desc in DEFINICION_LOGROS:
                session.add(
                    Logro(
                        tipo=tipo,
                        nombre=nombre,
                        descripcion=desc,
                        usuario_id=usuario_id,
                    )
                )
            session.commit()


def verificar_logros(usuario_id: int) -> None:
    with Session(engine) as session:
        gastos = session.exec(
            select(Gasto).where(Gasto.usuario_id == usuario_id)
        ).all()
        total = sum(g.monto for g in gastos)

        logros = session.exec(
            select(Logro).where(Logro.usuario_id == usuario_id)
        ).all()

        for logro in logros:
            if logro.tipo == TipoLogro.PRIMER_GASTO and len(gastos) >= 1:
                logro.desbloqueado = True
            elif logro.tipo == TipoLogro.CINCO_GASTOS and len(gastos) >= 5:
                logro.desbloqueado = True
            elif logro.tipo == TipoLogro.AHORRO_BAJO and 0 < total < 100:
                logro.desbloqueado = True

        session.commit()


def obtener_logros(usuario_id: int) -> list[Logro]:
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
                usuario_id=l.usuario_id,
            )
            for l in logros
        ]


# =========================
# FILTROS
# =========================


def aplicar_filtros(
    df: pd.DataFrame, categoria: str, fecha_min: date, fecha_max: date
) -> pd.DataFrame:
    if df.empty:
        return df
    fecha_min = pd.to_datetime(fecha_min)
    fecha_max = pd.to_datetime(fecha_max)
    if categoria != "Todas":
        df = df[df["Categoría"] == categoria]
    df = df[(df["Fecha"] >= fecha_min) & (df["Fecha"] <= fecha_max)]
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
    opcion = st.radio("", ["Iniciar sesión", "Crear cuenta"], horizontal=True)
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
    st.set_page_config(page_title="Control de Gastos Pro", layout="wide")
    crear_db()
    inicializar_auth()

    if st.session_state.usuario is None:
        pantalla_login()
        return

    usuario = st.session_state.usuario
    inicializar_logros(usuario.id)
    verificar_logros(usuario.id)

    # ── Sidebar ──────────────────────────────────────────────
    st.sidebar.title("Mis Finanzas")
    st.sidebar.write(f"**{usuario.username}**")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.usuario = None
        st.rerun()

    st.title("Control de Gastos")

    # ── Formulario ───────────────────────────────────────────
    st.subheader("Agregar gasto")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        concepto = st.text_input("Concepto")
    with col2:
        monto = st.number_input("Monto", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox(
            "Categoría", ["Comida", "Transporte", "Ocio", "Otros"]
        )
    with col4:
        fecha = st.date_input("Fecha", value=date.today())

    if st.button("Agregar", use_container_width=False):
        ok, msg = agregar_gasto(concepto, monto, categoria, fecha, usuario.id)
        (st.success if ok else st.warning)(msg)
        if ok:
            st.rerun()

    df = obtener_dataframe(usuario.id)
    st.divider()

    # ── Filtros ──────────────────────────────────────────────
    st.subheader("Filtros")
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        cat_filtro = st.selectbox(
            "Filtrar por categoría",
            ["Todas", "Comida", "Transporte", "Ocio", "Otros"],
        )
    with colf2:
        fecha_min = st.date_input("Desde", value=date(2024, 1, 1))
    with colf3:
        fecha_max = st.date_input("Hasta", value=date.today())

    df_filtrado = aplicar_filtros(df, cat_filtro, fecha_min, fecha_max)

    # ── Tabla ────────────────────────────────────────────────
    st.subheader("Datos")
    if not df_filtrado.empty:
        cols_mostrar = ["Concepto", "Monto", "Categoría", "Fecha"]
        cols_existentes = [c for c in cols_mostrar if c in df_filtrado.columns]
        st.dataframe(df_filtrado[cols_existentes], use_container_width=True)
    else:
        st.info("No hay gastos que coincidan con los filtros.")

    # ── Métricas ─────────────────────────────────────────────
    total = calcular_total(df_filtrado)
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Total gastado", f"${total:,.2f}")
    mc2.metric("Número de gastos", len(df_filtrado))
    if not df_filtrado.empty:
        mc3.metric("Promedio por gasto", f"${total / len(df_filtrado):,.2f}")

    # ── Gráficas ─────────────────────────────────────────────
    st.subheader("Visualización")
    if not df_filtrado.empty:
        colg1, colg2 = st.columns(2)
        with colg1:
            st.write("**Gasto por categoría**")
            st.bar_chart(df_filtrado.groupby("Categoría")["Monto"].sum())
        with colg2:
            st.write("**Gasto por fecha**")
            st.line_chart(df_filtrado.groupby("Fecha")["Monto"].sum())
    else:
        st.info("No hay datos para graficar.")

    # ── Logros ───────────────────────────────────────────────
    st.subheader("Logros")
    logros = obtener_logros(usuario.id)
    cols = st.columns(len(logros)) if logros else []
    for i, logro in enumerate(logros):
        with cols[i]:
            if logro.desbloqueado:
                st.success(f"**{logro.nombre}**\n\n{logro.descripcion}")
            else:
                st.warning(f"**{logro.nombre}**\n\n{logro.descripcion}")


if __name__ == "__main__":
    main()
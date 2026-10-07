"""Estructura fija de la pantalla principal: barra lateral, banner y tarjetas superiores."""
from datetime import date

import streamlit as st

from diseno.components import kpi
from base.config import MESES_ES, RUTA_DOCUMENTACION
from logica.presupuesto_service import verificar_alerta_presupuesto


# UI: barra lateral (perfil y cerrar sesión).
def render_sidebar(usuario) -> None:
    st.sidebar.title("Mis Finanzas")
    st.sidebar.download_button(
        "📖 Documentación",
        data=(RUTA_DOCUMENTACION).read_bytes(),
        file_name="documentacion.html",
        mime="text/html",
        use_container_width=True
    )
    # UI: tarjeta de perfil con la inicial del usuario.
    st.sidebar.markdown(
        f"""
        <div class="perfil">
            <div class="avatar">{usuario.username[:1].upper()}</div>
            <div>
                <div class="nombre">{usuario.username}</div>
                <div class="rol">Cuenta personal</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Cerrar sesión: borra al usuario de la sesión y recarga.
    if st.sidebar.button(
        "Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.usuario = None
        st.rerun()


# UI: banner de bienvenida con el mes actual.
def render_hero(usuario, hoy: date) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>Hola, {usuario.username} 👋</h1>
            <p>Resumen de {MESES_ES[hoy.month - 1]} de {hoy.year}. Aquí tienes el control de tus gastos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# UI + LÓGICA: tarjetas del mes actual (gastado, presupuesto y disponible).
def render_resumen_superior(usuario, hoy: date) -> None:
    alerta, acumulado, presupuesto = verificar_alerta_presupuesto(
        usuario.id,
        hoy.year,
        hoy.month
    )

    # UI: tres tarjetas: gastado este mes, presupuesto y disponible.
    r1, r2, r3 = st.columns(3)

    r1.markdown(
        kpi("Gastado este mes", f"${acumulado:,.2f}", destacada=True),
        unsafe_allow_html=True
    )
    r2.markdown(
        kpi(
            "Presupuesto del mes",
            f"${presupuesto:,.2f}" if presupuesto is not None else "Sin definir"
        ),
        unsafe_allow_html=True
    )
    if presupuesto is not None:
        r3.markdown(
            kpi("Disponible", f"${presupuesto - acumulado:,.2f}"),
            unsafe_allow_html=True
        )
    else:
        r3.markdown(
            kpi("Disponible", "—"),
            unsafe_allow_html=True
        )

    st.write("")

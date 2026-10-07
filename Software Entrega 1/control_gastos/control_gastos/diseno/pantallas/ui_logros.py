"""Pestaña LOGROS: tarjetas de logros ganados y por ganar."""
import streamlit as st

from diseno.components import titulo_seccion
from logica.logros_service import obtener_logros


# UI: contenido de la pestaña.
def render_tab_logros(usuario) -> None:
    st.write("")
    titulo_seccion("Logros", "Desbloquéalos usando la app.")

    # LÓGICA: logros del usuario.
    logros = obtener_logros(usuario.id)
    # UI: una columna por logro.
    cols = st.columns(len(logros)) if logros else []

    for i, logro in enumerate(logros):
        with cols[i]:
            # Desbloqueado: tarjeta dorada con medalla. Si no: tarjeta gris con candado.
            if logro.desbloqueado:
                st.markdown(
                    f"""
                    <div class="logro ganado">
                        <div class="sello">🏅</div>
                        <div class="nombre">{logro.nombre}</div>
                        <div class="desc">{logro.descripcion}</div>
                        <div class="estado">Desbloqueado</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="logro bloqueado">
                        <div class="sello">🔒</div>
                        <div class="nombre">{logro.nombre}</div>
                        <div class="desc">{logro.descripcion}</div>
                        <div class="estado">Por desbloquear</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

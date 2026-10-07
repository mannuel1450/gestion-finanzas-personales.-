"""Pestaña DOCUMENTACIÓN: muestra el archivo documentacion.html."""
import streamlit as st

from diseno.components import titulo_seccion
from base.config import RUTA_DOCUMENTACION


# UI: contenido de la pestaña.
def render_tab_documentacion() -> None:
    st.write("")
    titulo_seccion(
        "Documentación del Sistema",
        "Consulta la documentación técnica y manuales de usuario."
    )

    if RUTA_DOCUMENTACION.exists():
        # Lee el contenido del HTML en UTF-8
        html_contenido = RUTA_DOCUMENTACION.read_text(encoding="utf-8")

        # Muestra el contenido HTML incrustado en un contenedor scrolleable
        st.components.v1.html(html_contenido, height=900, scrolling=True)
    else:
        st.error("No se encontró el archivo documentacion.html en el directorio actual.")

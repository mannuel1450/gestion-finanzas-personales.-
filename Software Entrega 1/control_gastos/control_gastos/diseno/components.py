"""Componentes visuales reutilizables (tarjetas, títulos, estilo de gráficas)."""
import altair as alt
import streamlit as st


# UI: devuelve el HTML de una tarjeta de número (ej. 'Total gastado').
def kpi(etiqueta: str, valor: str, destacada: bool = False) -> str:
    clase = "kpi destacada" if destacada else "kpi"
    return (
        f'<div class="{clase}">'
        f'<div class="etiqueta">{etiqueta}</div>'
        f'<div class="valor">{valor}</div>'
        f'</div>'
    )


# UI: da a las gráficas letras claras y fondo transparente.
def estilo_grafica(chart: alt.Chart) -> alt.Chart:
    """Aplica estilo claro/transparente a una gráfica de Altair."""
    return (
        chart
        .configure(background="transparent")
        .configure_axis(
            labelColor="#F2F6FA",
            titleColor="#F2F6FA",
            gridColor="rgba(255,255,255,0.12)",
            domainColor="rgba(255,255,255,0.30)",
            tickColor="rgba(255,255,255,0.30)"
        )
        .configure_view(strokeWidth=0)
    )


# UI: escribe un título de sección con una descripción corta.
def titulo_seccion(titulo: str, subtitulo: str = "") -> None:
    st.markdown(f'<div class="titulo-seccion">{titulo}</div>', unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f'<div class="sub-seccion">{subtitulo}</div>', unsafe_allow_html=True)

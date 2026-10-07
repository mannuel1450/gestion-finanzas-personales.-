"""Punto de entrada: solo arma la pantalla llamando a los demás módulos.

Ejecutar con:  streamlit run app.py
"""
from datetime import date

import streamlit as st

from base.database import crear_db
from logica.logros_service import inicializar_logros, verificar_logros
from logica.gastos_service import obtener_dataframe
from diseno.styles import aplicar_estilos
from diseno.pantallas.ui_documentacion import render_tab_documentacion
from diseno.pantallas.ui_gastos import render_tab_gastos
from diseno.pantallas.ui_layout import render_hero, render_resumen_superior, render_sidebar
from diseno.pantallas.ui_login import inicializar_auth, pantalla_login
from diseno.pantallas.ui_logros import render_tab_logros
from diseno.pantallas.ui_presupuesto import render_tab_presupuesto
from diseno.pantallas.ui_resumen import render_tab_resumen

# PANTALLA PRINCIPAL: aquí se arma toda la app. Se ejecuta en cada interacción.
def main() -> None:
    # UI: título de la pestaña del navegador, ícono y ancho completo.
    st.set_page_config(
        page_title="Control de Gastos Pro",
        page_icon="💸",
        layout="wide"
    )

    # UI: carga los estilos visuales.
    aplicar_estilos()
    # LÓGICA: asegura que la base de datos y sus tablas existan.
    crear_db()
    # LÓGICA: prepara la variable de sesión del usuario.
    inicializar_auth()

    # Si nadie ha iniciado sesión, muestra el login y se detiene aquí.
    if st.session_state.usuario is None:
        pantalla_login()
        return

    # Usuario que está usando la app ahora.
    usuario = st.session_state.usuario

    # LÓGICA: crea los logros que falten y revisa si se desbloqueó alguno nuevo.
    inicializar_logros(usuario.id)
    nuevos_logros = verificar_logros(usuario.id)

    # UI: mensaje verde por cada logro desbloqueado.
    for nombre_logro in nuevos_logros:
        st.success(f"🏆 ¡Logro desbloqueado!: {nombre_logro}")

    # Estructura fija: barra lateral, banner y tarjetas del mes.
    render_sidebar(usuario)
    hoy = date.today()
    render_hero(usuario, hoy)
    render_resumen_superior(usuario, hoy)

    # LÓGICA: todos los gastos del usuario en una tabla (se reutiliza en las pestañas).
    df = obtener_dataframe(usuario.id)

    # UI: las pestañas. Cada una se dibuja en su propio módulo.
    tab_resumen, tab_gastos, tab_presupuesto, tab_logros, tab_documentacion = st.tabs(
        ["📊  Resumen", "➕  Gastos", "🎯  Presupuesto", "🏆  Logros", "📖  Documentación"]
    )

    with tab_gastos:
        render_tab_gastos(usuario, df)

    with tab_presupuesto:
        render_tab_presupuesto(usuario)

    with tab_resumen:
        render_tab_resumen(df)

    with tab_logros:
        render_tab_logros(usuario)

    with tab_documentacion:
        render_tab_documentacion()


# Punto de entrada: sirve tanto con 'streamlit run app.py' como con el botón de Run.
if __name__ == "__main__":
    from streamlit import runtime

    if runtime.exists():
        # Ya estamos dentro de Streamlit: dibuja la app.
        main()
    else:
        # Se ejecutó con Python normal: se relanza con Streamlit.
        import subprocess
        import sys
        from pathlib import Path

        carpeta = Path(__file__).parent
        try:
            subprocess.run(
                [sys.executable, "-m", "streamlit", "run", "app.py"],
                cwd=carpeta
            )
        except KeyboardInterrupt:
            pass
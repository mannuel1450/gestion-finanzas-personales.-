"""Pestaña GASTOS: agregar, eliminar y exportar."""
from datetime import date

import streamlit as st

from diseno.components import titulo_seccion
from base.config import ICONOS_CATEGORIA
from herramientas.exportacion import exportar_gastos_csv
from logica.gastos_service import agregar_gasto, eliminar_gasto


# UI: contenido de la pestaña.
def render_tab_gastos(usuario, df) -> None:
    st.write("")
    # UI: formulario para agregar un gasto.
    titulo_seccion("Agregar gasto", "Anota lo que gastaste en segundos.")

    with st.container(key="glass2"):
        # UI: cuatro campos en una fila: concepto, monto, categoría y fecha.
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            concepto = st.text_input("Concepto", placeholder="Ej. Tacos")

        with col2:
            monto = st.number_input(
                "Monto",
                min_value=0.0,
                step=10.0
            )

        with col3:
            categoria = st.selectbox(
                "Categoría",
                ["Comida", "Transporte", "Ocio", "Otros"],
                format_func=lambda c: f"{ICONOS_CATEGORIA.get(c, '')} {c}"
            )

        with col4:
            fecha = st.date_input(
                "Fecha",
                value=date.today()
            )

        # Al presionar: LÓGICA valida y guarda; UI muestra el resultado y recarga si salió bien.
        if st.button("Agregar gasto", use_container_width=False):
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

    st.write("")
    # UI: sección para eliminar un gasto.
    titulo_seccion("Eliminar gasto", "Elige un gasto y confirma para borrarlo.")

    with st.container(key="glass3"):
        # Solo muestra el selector si hay gastos.
        if not df.empty:
            # Lista de gastos para elegir: el texto que se ve -> el ID real del gasto.
            opciones = {
                f"#{int(row['ID'])} — {row['Concepto']} — "
                f"${float(row['Monto']):,.2f}": int(row["ID"])
                for _, row in df.iterrows()
            }

            gasto_seleccionado = st.selectbox(
                "Selecciona el gasto que deseas eliminar",
                list(opciones.keys())
            )

            # Casilla de confirmación para evitar borrar por error.
            confirmar = st.checkbox(
                "Confirmo que deseo eliminar este gasto."
            )

            # Al presionar: exige confirmar y luego llama a la lógica para borrar.
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
            st.info("Aún no tienes gastos. Agrega el primero arriba.")

    st.write("")
    # UI: sección para descargar los gastos.
    titulo_seccion("Exportar gastos", "Descarga todos tus gastos en un archivo CSV.")

    with st.container(key="glass4"):
        # Genera el CSV (LÓGICA) y muestra el botón para descargarlo (UI).
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

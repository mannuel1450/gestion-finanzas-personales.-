"""Pestaña RESUMEN: filtros, métricas, gráficas y tabla."""
from datetime import date

import altair as alt
import streamlit as st

from diseno.components import kpi, estilo_grafica, titulo_seccion
from herramientas.filtros import aplicar_filtros, calcular_total


# UI: contenido de la pestaña.
def render_tab_resumen(df) -> None:
    st.write("")
    # UI: filtros por categoría y fechas.
    titulo_seccion("Filtros", "Acota tus gastos por categoría y fechas.")

    with st.container(key="glass7"):
        # UI: tres campos: categoría, fecha inicial y fecha final.
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

    # LÓGICA: aplica los filtros a la tabla; todo lo de abajo usa esta tabla filtrada.
    df_filtrado = aplicar_filtros(
        df,
        cat_filtro,
        fecha_min,
        fecha_max
    )

    st.write("")

    # ── Métricas ────────────────────────────────────────
    # LÓGICA: total gastado con los filtros actuales.
    total = calcular_total(df_filtrado)

    # UI: tarjetas con total, número de gastos y promedio por gasto.
    mc1, mc2, mc3 = st.columns(3)

    mc1.markdown(
        kpi("Total gastado", f"${total:,.2f}", destacada=True),
        unsafe_allow_html=True
    )

    mc2.markdown(
        kpi("Número de gastos", f"{len(df_filtrado)}"),
        unsafe_allow_html=True
    )

    if not df_filtrado.empty:
        mc3.markdown(
            kpi("Promedio por gasto", f"${total / len(df_filtrado):,.2f}"),
            unsafe_allow_html=True
        )
    else:
        mc3.markdown(kpi("Promedio por gasto", "—"), unsafe_allow_html=True)

    st.write("")

    # ── Gráficas ────────────────────────────────────────
    # UI: gráficas.
    titulo_seccion("Visualización", "Dónde y cuándo se va tu dinero.")

    if not df_filtrado.empty:
        colg1, colg2 = st.columns(2)

        with colg1:
            with st.container(key="glass8"):
                st.write("**Gasto por categoría**")
                # LÓGICA: suma de gastos por categoría (para la gráfica de barras).
                datos_cat = (
                    df_filtrado.groupby("Categoría")["Monto"]
                    .sum()
                    .reset_index()
                )
                # UI: gráfica de barras (categorías en X, monto en Y).
                grafica_cat = alt.Chart(datos_cat).mark_bar(
                    color="#5EEAD4",
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6
                ).encode(
                    x=alt.X("Categoría:N", sort="-y",
                            axis=alt.Axis(labelAngle=0, title=None)),
                    y=alt.Y("Monto:Q", title=None),
                    tooltip=["Categoría", "Monto"]
                )
                st.altair_chart(
                    estilo_grafica(grafica_cat),
                    use_container_width=True,
                    theme=None
                )

        with colg2:
            with st.container(key="glass9"):
                st.write("**Gasto por fecha**")
                # LÓGICA: suma de gastos por día (para la gráfica de línea).
                datos_fecha = (
                    df_filtrado.groupby("Fecha")["Monto"]
                    .sum()
                    .reset_index()
                )
                # UI: gráfica de línea (fecha en X, monto en Y).
                grafica_fecha = alt.Chart(datos_fecha).mark_line(
                    color="#F2A83B",
                    point=alt.OverlayMarkDef(color="#F2A83B")
                ).encode(
                    x=alt.X("Fecha:T", title=None),
                    y=alt.Y("Monto:Q", title=None),
                    tooltip=["Fecha", "Monto"]
                )
                st.altair_chart(
                    estilo_grafica(grafica_fecha),
                    use_container_width=True,
                    theme=None
                )
    else:
        st.info("No hay datos para graficar.")

    st.write("")

    # ── Tabla ────────────────────────────────────────────
    # UI: tabla con los gastos que cumplen los filtros.
    titulo_seccion("Datos", "Todos los gastos que coinciden con tus filtros.")

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

        # UI: la tabla (sin índice, con formato de dinero y de fecha).
        st.dataframe(
            df_filtrado[cols_existentes],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Monto": st.column_config.NumberColumn(
                    "Monto",
                    format="$%.2f"
                ),
                "Fecha": st.column_config.DateColumn(
                    "Fecha",
                    format="DD/MM/YYYY"
                ),
            }
        )
    else:
        st.info("No hay gastos que coincidan con los filtros.")

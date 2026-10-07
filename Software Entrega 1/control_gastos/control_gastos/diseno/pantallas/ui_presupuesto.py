"""Pestaña PRESUPUESTO: definir el límite del mes y ver el avance."""
from datetime import date

import streamlit as st

from diseno.components import titulo_seccion
from base.config import MESES_ES
from logica.presupuesto_service import (
    guardar_presupuesto,
    obtener_presupuesto,
    verificar_alerta_presupuesto,
)


# UI: contenido de la pestaña.
def render_tab_presupuesto(usuario) -> None:
    hoy = date.today()

    st.write("")
    # UI: título de la sección de presupuesto.
    titulo_seccion(
        "Presupuesto mensual",
        f"Define cuánto quieres gastar en {MESES_ES[hoy.month - 1]} de {hoy.year}."
    )

    # LÓGICA: presupuesto ya guardado para este mes (si existe).
    presupuesto_actual = obtener_presupuesto(
        usuario.id,
        hoy.year,
        hoy.month
    )

    with st.container(key="glass5"):
        if presupuesto_actual is not None:
            st.info(
                f"Presupuesto de {MESES_ES[hoy.month - 1]} de {hoy.year}: "
                f"${presupuesto_actual:,.2f}"
            )

        # UI: campo para escribir el presupuesto del mes.
        presupuesto_input = st.number_input(
            "Define tu presupuesto para el mes actual",
            min_value=0.0,
            step=100.0,
            value=float(presupuesto_actual or 0.0)
        )

        # Al presionar: LÓGICA lo guarda; UI avisa y recarga.
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

    st.write("")

    # LÓGICA: vuelve a calcular cuánto se lleva gastado vs. el presupuesto.
    alerta, acumulado, presupuesto = verificar_alerta_presupuesto(
        usuario.id,
        hoy.year,
        hoy.month
    )

    if presupuesto is not None:
        # Porcentaje usado (máximo 100) para la barra de progreso.
        porcentaje = min(acumulado / presupuesto, 1.0) * 100

        # Color de la barra: verde normal, ámbar desde 75%, rojo al llegar a 100%.
        if porcentaje >= 100:
            color_barra = "var(--coral)"
        elif porcentaje >= 75:
            color_barra = "var(--ambar)"
        else:
            color_barra = "var(--menta)"

        # UI: barra de progreso del presupuesto.
        with st.container(key="glass6"):
            st.markdown(
                f"""
                <div class="barra-fondo">
                    <div class="barra-relleno" style="width:{porcentaje:.1f}%; background:{color_barra};"></div>
                </div>
                <div class="barra-datos">
                    <span>{porcentaje:.0f}% usado</span>
                    <span>${acumulado:,.2f} de ${presupuesto:,.2f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        # Mensaje de alerta si ya se pasó; si no, resumen de lo que queda disponible.
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

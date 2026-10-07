"""Pantalla de acceso (iniciar sesión / crear cuenta) y estado de sesión."""
import streamlit as st

from logica.auth_service import registrar_usuario, login_usuario


# LÓGICA: prepara la sesión; 'usuario' vacío significa que nadie ha entrado.
def inicializar_auth() -> None:
    if "usuario" not in st.session_state:
        st.session_state.usuario = None


# UI + LÓGICA: pantalla de acceso (iniciar sesión o crear cuenta).
def pantalla_login() -> None:
    # UI: columna central para que el formulario quede en medio.
    _, centro, _ = st.columns([1, 1.2, 1])

    with centro:
        # UI: logo y título de la pantalla de acceso.
        st.markdown(
            """
            <div class="login-marca">
                <div class="logo">💸</div>
                <h1>Control de Gastos</h1>
                <p>Registra, entiende y controla tu dinero.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # UI: tarjeta de cristal que contiene el formulario.
        with st.container(key="glass1"):
            # UI: elegir entre 'Iniciar sesión' y 'Crear cuenta'.
            opcion = st.radio(
                "Acceso",
                ["Iniciar sesión", "Crear cuenta"],
                horizontal=True,
                label_visibility="collapsed"
            )

            # UI: campos de usuario y contraseña.
            username = st.text_input("Usuario", placeholder="Tu nombre de usuario")
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )

            # Si eligió crear cuenta: registra al usuario y muestra el resultado.
            if opcion == "Crear cuenta":
                if st.button("Registrarse", use_container_width=True):
                    ok, msg = registrar_usuario(username, password)
                    (st.success if ok else st.error)(msg)

            else:
                # Si eligió iniciar sesión: valida y, si es correcto, guarda al usuario en la sesión.
                if st.button("Entrar", use_container_width=True):
                    user = login_usuario(username, password)

                    if user:
                        st.session_state.usuario = user
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

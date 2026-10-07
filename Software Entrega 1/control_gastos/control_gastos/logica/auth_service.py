"""Lógica de usuarios: registro e inicio de sesión."""
from typing import Optional

from sqlmodel import Session, select

from base.database import engine
from base.models import Usuario
from base.security import hash_password, verificar_password


# LÓGICA: crea una cuenta nueva. Devuelve (True/False, mensaje).
def registrar_usuario(username: str, password: str) -> tuple[bool, str]:
    """Registra usuario. Retorna (éxito, mensaje)."""
    # Validaciones: usuario de 3+ caracteres y contraseña de 6+.
    if not username or len(username.strip()) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if not password or len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    with Session(engine) as session:
        # Revisa que el nombre de usuario no esté repetido.
        existente = session.exec(
            select(Usuario).where(Usuario.username == username.strip())
        ).first()

        if existente:
            return False, "Ese nombre de usuario ya está registrado."

        # Crea el usuario con la contraseña ya encriptada y lo guarda.
        nuevo = Usuario(
            username=username.strip(),
            password=hash_password(password)
        )
        session.add(nuevo)
        session.commit()

        return True, "Usuario creado correctamente."


# LÓGICA: busca al usuario y revisa su contraseña. Devuelve el usuario o None.
def login_usuario(username: str, password: str) -> Optional[Usuario]:
    """Retorna el objeto Usuario si las credenciales son válidas."""
    with Session(engine) as session:
        # Busca el usuario por su nombre.
        user = session.exec(
            select(Usuario).where(Usuario.username == username.strip())
        ).first()

        # Si existe y la contraseña coincide, devuelve sus datos.
        if user and verificar_password(password, user.password):
            session.refresh(user)
            return Usuario(
                id=user.id,
                username=user.username,
                password=user.password
            )

        return None

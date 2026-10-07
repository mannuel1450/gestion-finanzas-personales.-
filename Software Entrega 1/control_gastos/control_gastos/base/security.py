"""Seguridad: encriptado y verificación de contraseñas."""
import bcrypt


# LÓGICA: convierte la contraseña en un código seguro antes de guardarla.
def hash_password(password: str) -> str:
    """Genera hash bcrypt con salt automático."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# LÓGICA: compara la contraseña escrita con la guardada (sin desencriptar).
def verificar_password(password: str, hashed: str) -> bool:
    """Verifica contraseña contra hash bcrypt."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

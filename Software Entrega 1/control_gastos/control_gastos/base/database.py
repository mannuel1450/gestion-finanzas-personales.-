"""Conexión a la base de datos y creación de tablas."""
from sqlmodel import SQLModel, create_engine

from base.config import DB_URL
import base.models as models  # noqa: F401  (registra las tablas en SQLModel.metadata)


# LÓGICA: conexión a la base de datos (se guarda en el archivo gastos.db).
engine = create_engine(DB_URL, echo=False)


# LÓGICA: crea las tablas en la base de datos si todavía no existen.
def crear_db():
    SQLModel.metadata.create_all(engine)

"""Modelos (tablas de la base de datos). Solo definen la estructura de los datos."""
from datetime import date
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


# LÓGICA: lista fija de los tipos de logro que existen.
class TipoLogro(str, Enum):
    PRIMER_GASTO = "primer_gasto"
    CINCO_GASTOS = "cinco_gastos"
    AHORRO_BAJO = "ahorro_bajo"


    TRES_DIAS_SEGUIDOS = "tres_dias_seguidos"
    DIEZ_GASTOS = "diez_gastos"


# LÓGICA: tabla 'usuario' (quién puede entrar). La contraseña se guarda encriptada.
class Usuario(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


# LÓGICA: tabla 'gasto' (cada gasto pertenece a un usuario).
class Gasto(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    concepto: str
    monto: float
    categoria: str
    fecha: date
    usuario_id: int = Field(foreign_key="usuario.id")


# LÓGICA: tabla 'presupuesto' (monto máximo por usuario, año y mes).
class Presupuesto(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    anio: int
    mes: int
    monto: float


# LÓGICA: tabla 'logro' (logros de cada usuario y si ya los desbloqueó).
class Logro(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: TipoLogro
    nombre: str
    descripcion: str
    desbloqueado: bool = False
    usuario_id: int = Field(foreign_key="usuario.id")

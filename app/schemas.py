from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    email: EmailStr
    rol: str = "cliente"


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        orm_mode = True


# ---------- Emprendedor ----------
class EmprendedorBase(BaseModel):
    nombre: str
    apellido: str
    negocio: str
    descripcion: Optional[str] = None


class EmprendedorCreate(EmprendedorBase):
    usuario_id: int


class EmprendedorResponse(EmprendedorBase):
    id: int
    usuario: UsuarioResponse

    class Config:
        orm_mode = True


# ---------- Servicio ----------
class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class ServicioCreate(ServicioBase):
    emprendedor_id: int


class ServicioResponseCreate(ServicioBase):
    id: int

    class Config:
        orm_mode = True


# ---------- Turno ----------
class TurnoBase(BaseModel):
    fecha_hora_inicio: datetime
    duracion_minutos: int
    capacidad: int
    precio: Optional[float] = None


class TurnoCreate(TurnoBase):
    servicio_id: int


class TurnoResponseCreate(TurnoBase):
    id: int

    class Config:
        orm_mode = True


class TurnoResponse(BaseModel):
    id: int
    fecha_hora_inicio: datetime
    capacidad: int
    precio: Optional[float]

    class Config:
        orm_mode = True


class ServicioResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    turnos: List[TurnoResponse] = []

    class Config:
        orm_mode = True


# ---------- Reserva ----------
class ReservaBase(BaseModel):
    turno_id: int
    usuario_id: int


class ReservaCreate(ReservaBase):
    pass


class ReservaResponse(ReservaBase):
    id: int

    class Config:
        orm_mode = True

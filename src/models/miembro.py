from typing import Optional
import strawberry


@strawberry.type
class Miembro:
    id: Optional[str] = None
    nombre: str
    apellido: str
    edad: int    
    email: str
    fecha_bautizmo: Optional[str] = None
    ubicacion: str
    telefono: int
    estado: Optional[str] = None
    usuario_id: str

@strawberry.input
class MiembroInput:
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    edad: Optional[int] = None    
    email: Optional[str] = None
    fecha_bautizmo: Optional[str] = None
    ubicacion: Optional[str] = None
    telefono: Optional[int] = None
    estado: Optional[str] = None
    usuario_id: Optional[str] = None

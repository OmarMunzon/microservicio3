from typing import Optional
import strawberry


@strawberry.type
class Usuario:
    id: Optional[str] = None
    username: str
    correo: str
    password: Optional[str] = None
    fecha_registro: str

@strawberry.input
class UsuarioInput:
    username: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None
    fecha_registro: Optional[str] = None

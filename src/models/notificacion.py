from typing import Optional
import strawberry


@strawberry.type
class Notificacion:
    id: Optional[str] = None
    mensaje: str
    fecha_envio: Optional[str] = None
    miembro_id: str

@strawberry.input
class NotificacionInput:
    mensaje: Optional[str] = None
    fecha_envio: Optional[str] = None
    miembro_id: Optional[str] = None
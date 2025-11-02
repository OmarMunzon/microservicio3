from typing import List, Optional
from src.models.notificacion import Notificacion, NotificacionInput
from src.models.miembro import Miembro, MiembroInput
from src.models.usuario import Usuario, UsuarioInput
import strawberry
from src.db.database import db
from strawberry.types import Info
from datetime import datetime
from strawberry import Schema


@strawberry.type
class Query:
    @strawberry.field
    def usuarios(self) -> List[Usuario]:
        """Obtener todos los usuarios"""
        usuarios_ref = db.collection('usuarios')
        docs = usuarios_ref.stream()
        return [Usuario(**doc.to_dict(), id=doc.id) for doc in docs]

    @strawberry.field
    def usuario(self, id: str, info: Info) -> Optional[Usuario]:
        """Obtener un usuario por ID"""
        doc = db.collection('usuarios').document(id).get()
        if doc.exists:
            return Usuario(**doc.to_dict(), id=doc.id)
        return None

    @strawberry.field
    def miembros(self) -> List[Miembro]:
        """Obtener todos los miembros"""
        miembros_ref = db.collection('miembros')
        docs = miembros_ref.stream()
        return [Miembro(**doc.to_dict(), id=doc.id) for doc in docs]

    @strawberry.field
    def miembro(self, id: str, info: Info) -> Optional[Miembro]:
        """Obtener un miembro por ID"""
        doc = db.collection('miembros').document(id).get()
        if doc.exists:
            return Miembro(**doc.to_dict(), id=doc.id)
        return None


    @strawberry.field
    def notificaciones(self) -> List[Notificacion]:
        """Obtener todos los notificaciones"""
        notificaciones_ref = db.collection('notificaciones')
        docs = notificaciones_ref.stream()
        return [Notificacion(**doc.to_dict(), id=doc.id) for doc in docs]

    @strawberry.field
    def notificacion(self, id: str, info: Info) -> Optional[Notificacion]:
        """Obtener una notificacion por ID"""
        doc = db.collection('notificaciones').document(id).get()
        if doc.exists:
            return Notificacion(**doc.to_dict(), id=doc.id)
        return None



@strawberry.type
class Mutation:
    @strawberry.mutation
    def crear_usuario(self, usuario: UsuarioInput) -> Usuario:
        """Crear un nuevo usuario"""
        # Verificar duplicado
        existing = db.collection('usuarios').where('correo', '==', usuario.correo).get()
        if existing:
            raise Exception("Correo ya registrado")

        # Hashear password y setear fecha
        #hashed_password = pwd_context.hash(usuario.password)        
        if not usuario.fecha_registro:
            fecha = datetime.now().isoformat()
        else:
            fecha = usuario.fecha_registro

        data = {
            "username": usuario.username,
            "correo": usuario.correo,
            "password": usuario.password,
            "fecha_registro": fecha
        }
        doc_ref = db.collection('usuarios').add(data)
        doc_id = doc_ref[1].id

        # Retornar sin password
        return Usuario(id=doc_id, username=usuario.username, correo=usuario.correo, fecha_registro=fecha)

    @strawberry.mutation
    def actualizar_usuario(self, id: str, usuario: UsuarioInput) -> Optional[Usuario]:
        """Actualizar un usuario (sin cambiar password por simplicidad)"""
        doc_ref = db.collection('usuarios').document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("Usuario no encontrado")

        data = {
            "username": usuario.username,
            "correo": usuario.correo,
            "fecha_registro": usuario.fecha_registro or doc.to_dict().get('fecha_registro')
        }
        doc_ref.update(data)
        return Usuario(id=id, **data)

    @strawberry.mutation
    def eliminar_usuario(self, id: str) -> bool:
        """Eliminar un usuario"""
        doc_ref = db.collection('usuarios').document(id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False


    @strawberry.mutation
    def crear_miembro(self, miembro: MiembroInput) -> Miembro:
        """Crear un nuevo miembro"""
        usuario_doc = db.collection('usuarios').document(miembro.usuario_id).get()
        if not usuario_doc.exists:
            raise Exception("Usuario no encontrado")
        
        existing = db.collection('miembros').where('email', '==', miembro.email).get()
        if existing:
            raise Exception("Correo ya registrado")
      
        if not miembro.fecha_bautizmo:
            fecha = datetime.now().isoformat()
        else:
            fecha = miembro.fecha_bautizmo

        data = {
            "nombre": miembro.nombre,
            "apellido": miembro.apellido,
            "edad": miembro.edad,
            "fecha_bautizmo": fecha,
            "email": miembro.email,
            "ubicacion": miembro.ubicacion,
            "telefono": miembro.telefono,
            "estado": miembro.estado,
            "usuario_id": miembro.usuario_id
        }
        doc_ref = db.collection('miembros').add(data)
        doc_id = doc_ref[1].id

        # Retornar
        return Miembro(id=doc_id, nombre=miembro.nombre, apellido=miembro.apellido, edad=miembro.edad, fecha_bautizmo=fecha, email=miembro.email, ubicacion=miembro.ubicacion, telefono=miembro.telefono, estado=miembro.estado, usuario_id=miembro.usuario_id)

    @strawberry.mutation
    def actualizar_miembro(self, id: str, miembro: MiembroInput) -> Optional[Miembro]:
        """Actualizar un miembro"""
        doc_ref = db.collection('miembros').document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("Miembro no encontlrado")

        data = { 
            "nombre": miembro.nombre,
            "apellido": miembro.apellido,
            "edad": miembro.edad,
            "email": miembro.email,
            "ubicacion": miembro.ubicacion,
            "fecha_bautizmo": miembro.fecha_bautizmo or doc.to_dict().get('fecha_bautizmo'),
            "telefono": miembro.telefono,
            "estado": miembro.estado,
            "usuario_id": miembro.usuario_id            
        }
        doc_ref.update(data)
        return Miembro(id=id, **data)

    @strawberry.mutation
    def eliminar_miembro(self, id: str) -> bool:
        """Eliminar un miembro"""
        doc_ref = db.collection('miembros').document(id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False

    @strawberry.mutation
    def crear_notificacion(self, notificacion: NotificacionInput) -> Notificacion:
        """Crear una nuevo notificacion"""
        miembro_doc = db.collection('miembros').document(notificacion.miembro_id).get()
        if not miembro_doc.exists:
            raise Exception("Miembro no encontrado")

        if not notificacion.fecha_envio:
            fecha = datetime.now().isoformat()
        else:
            fecha = notificacion.fecha_envio

        data = {
            "mensaje": notificacion.mensaje,
            "fecha_envio": fecha,
            "miembro_id": notificacion.miembro_id
        }
        doc_ref = db.collection('notificaciones').add(data)
        doc_id = doc_ref[1].id

        # Retornar
        return Notificacion(id=doc_id, mensaje=notificacion.mensaje, fecha_envio=fecha, miembro_id=notificacion.miembro_id)

    @strawberry.mutation
    def actualizar_notificacion(self, id: str, usuario: NotificacionInput) -> Optional[Notificacion]:
        """Actualizar una notificacion"""
        doc_ref = db.collection('notificaciones').document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("Notificacion no encontrado")

        data = {
            "mensaje": usuario.mensaje,
            "fecha_envio": usuario.fecha_envio or doc.to_dict().get('fecha_envio'),
            "miembro_id": usuario.miembro_id            
        }
        doc_ref.update(data)
        return Notificacion(id=id, **data)

    @strawberry.mutation
    def eliminar_notificacion(self, id: str) -> bool:
        """Eliminar una notificacion"""
        doc_ref = db.collection('notificaciones').document(id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False

# Crear el esquema
schema = Schema(query=Query, mutation=Mutation)



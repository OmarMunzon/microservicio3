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

        # Obtener datos existentes
        existing_data = doc.to_dict()

        # Construir data solo con campos proporcionados (no None)
        data = {}
        if usuario.username is not None:
            data["username"] = usuario.username
        if usuario.correo is not None:
            data["correo"] = usuario.correo
        if usuario.password is not None:  # Opcional: si quisieras permitirlo en el futuro
            data["password"] = usuario.password  # Nota: hashea antes de guardar en prod
        if usuario.fecha_registro is not None:
            data["fecha_registro"] = usuario.fecha_registro
        # Si fecha_registro no se proporciona, no la tocamos (Firestore preserva)

        # Si no hay cambios, no actualizar
        if not data:
            return Usuario.from_pydantic(Usuario(**existing_data, id=id))  # O construye manualmente

        doc_ref.update(data)

        # Retornar el usuario actualizado (combina existing + data)
        updated_data = {**existing_data, **data}
        return Usuario(id=id, **updated_data)
    

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
        """Actualizar un miembro (actualización parcial)"""
        doc_ref = db.collection('miembros').document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("Miembro no encontrado")

        # Obtener datos existentes
        existing_data = doc.to_dict()

        # Construir data solo con campos proporcionados (no None)
        data = {}
        if miembro.nombre is not None:
            data["nombre"] = miembro.nombre
        if miembro.apellido is not None:
            data["apellido"] = miembro.apellido
        if miembro.edad is not None:
            data["edad"] = miembro.edad
        if miembro.email is not None:
            data["email"] = miembro.email
        if miembro.ubicacion is not None:
            data["ubicacion"] = miembro.ubicacion
        if miembro.fecha_bautizmo is not None:
            data["fecha_bautizmo"] = miembro.fecha_bautizmo
        # Si no se proporciona, no la tocamos (preserva existente)
        if miembro.telefono is not None:
            data["telefono"] = miembro.telefono
        if miembro.estado is not None:
            data["estado"] = miembro.estado
        if miembro.usuario_id is not None:
            data["usuario_id"] = miembro.usuario_id  # Valida si es necesario (ej. no cambiar a otro usuario)

        # Si no hay cambios, retornar el actual sin actualizar
        if not data:
            return Miembro(id=id, **existing_data)

        doc_ref.update(data)

        # Retornar el miembro actualizado (combina existing + data)
        updated_data = {**existing_data, **data}
        return Miembro(id=id, **updated_data)

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
    def actualizar_notificacion(self, id: str, notificacion: NotificacionInput) -> Optional[Notificacion]:
        """Actualizar una notificación (actualización parcial)"""
        doc_ref = db.collection('notificaciones').document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("Notificación no encontrada")

        # Obtener datos existentes
        existing_data = doc.to_dict()

        # Construir data solo con campos proporcionados (no None)
        data = {}
        if notificacion.mensaje is not None:
            data["mensaje"] = notificacion.mensaje
        if notificacion.fecha_envio is not None:
            data["fecha_envio"] = notificacion.fecha_envio
        # Si no se proporciona, no la tocamos (preserva existente)
        if notificacion.miembro_id is not None:
            data["miembro_id"] = notificacion.miembro_id  # Valida si es necesario (ej. existencia del miembro)

        # Si no hay cambios, retornar el actual sin actualizar
        if not data:
            return Notificacion(id=id, **existing_data)

        doc_ref.update(data)

        # Retornar la notificación actualizada (combina existing + data)
        updated_data = {**existing_data, **data}
        return Notificacion(id=id, **updated_data)

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



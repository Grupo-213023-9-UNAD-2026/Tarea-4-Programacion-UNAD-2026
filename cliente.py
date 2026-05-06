"""
cliente.py
Autor: Paula Nikoll Arteta Guillen
Curso: Programación 213023 - UNAD
==========
Contiene la clase abstracta Entidad, la clase Cliente y el gestor
encargado de administrar clientes en memoria.
"""

# Importamos expresiones regulares para validar nombre y email.
import re
# Importamos utilidades para construir una clase abstracta base.
from abc import ABC, abstractmethod

# Importamos las excepciones específicas del dominio de clientes.
from excepciones import (
    ErrorClienteEmailInvalido,
    ErrorClienteIdentificacionInvalida,
    ErrorClienteNoEncontrado,
    ErrorClienteNombreInvalido,
    ErrorClienteYaExiste,
)
# Importamos el logger del proyecto para registrar eventos relevantes.
import logger


# Definimos el patrón aceptado para nombres con letras, espacios y tildes.
PATRON_NOMBRE = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$")
# Definimos el patrón básico aceptado para correos electrónicos.
PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")


# Esta clase abstracta representa cualquier entidad con ID y descripción.
class Entidad(ABC):
    """Contrato mínimo para las entidades del sistema."""

    @abstractmethod
    def obtener_id(self) -> str:
        # Este método obliga a cada entidad a exponer su identificador.
        raise NotImplementedError

    @abstractmethod
    def describir(self) -> str:
        # Este método obliga a cada entidad a devolver una descripción legible.
        raise NotImplementedError

    def __repr__(self) -> str:
        # Esta representación ayuda cuando se inspecciona el objeto en depuración.
        return f"<{self.__class__.__name__} id={self.obtener_id()}>"


# Esta clase modela un cliente registrado dentro del sistema.
class Cliente(Entidad):
    """Representa a un cliente con estado activo o inactivo."""

    def __init__(self, numero_id: str, nombre: str, email: str, telefono: str = ""):
        # Validamos la identificación antes de guardar el dato.
        self.__validar_identificacion(numero_id)
        # Validamos el nombre antes de usarlo dentro del objeto.
        self.__validar_nombre(nombre)
        # Validamos el correo antes de normalizarlo.
        self.__validar_email(email)
        # Guardamos la identificación sin espacios externos.
        self.__id = numero_id.strip()
        # Guardamos el nombre sin espacios sobrantes.
        self.__nombre = nombre.strip()
        # Guardamos el email en minúsculas para evitar duplicados por formato.
        self.__email = email.strip().lower()
        # Guardamos el teléfono o una cadena vacía si no se informó.
        self.__telefono = telefono.strip()
        # El cliente se crea activo por defecto.
        self.__activo = True
        # Registramos la creación para dejar trazabilidad en el log.
        logger.info(
            f"Cliente registrado: {self.__nombre} | ID: {self.__id} | Email: {self.__email}"
        )

    def __validar_identificacion(self, numero_id: str) -> None:
        # Rechazamos identificaciones vacías o compuestas solo por espacios.
        if not numero_id or not numero_id.strip():
            raise ErrorClienteIdentificacionInvalida(numero_id)

    def __validar_nombre(self, nombre: str) -> None:
        # Rechazamos nombres vacíos o compuestos solo por espacios.
        if not nombre or not nombre.strip():
            raise ErrorClienteNombreInvalido(nombre)
        # Rechazamos nombres con números o símbolos no permitidos.
        if not PATRON_NOMBRE.match(nombre.strip()):
            raise ErrorClienteNombreInvalido(nombre)

    def __validar_email(self, email: str) -> None:
        # Rechazamos correos vacíos para no dejar datos incompletos.
        if not email or not email.strip():
            raise ErrorClienteEmailInvalido(email)
        # Rechazamos correos que no cumplen el patrón mínimo esperado.
        if not PATRON_EMAIL.match(email.strip()):
            raise ErrorClienteEmailInvalido(email)

    def obtener_id(self) -> str:
        # Devolvemos la identificación única del cliente.
        return self.__id

    def describir(self) -> str:
        # Convertimos el estado booleano a una etiqueta más amigable.
        estado = "Activo" if self.__activo else "Inactivo"
        # Armamos una descripción detallada pensada para consola o reportes.
        return (
            "Cliente\n"
            f"  Identificacion : {self.__id}\n"
            f"  Nombre         : {self.__nombre}\n"
            f"  Email          : {self.__email}\n"
            f"  Telefono       : {self.__telefono or 'No registrado'}\n"
            f"  Estado         : {estado}"
        )

    @property
    def nombre(self) -> str:
        # Permitimos lectura controlada del nombre.
        return self.__nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        # Validamos el nuevo nombre antes de reemplazar el anterior.
        self.__validar_nombre(nuevo_nombre)
        # Guardamos la versión limpia del nombre recibido.
        self.__nombre = nuevo_nombre.strip()
        # Registramos el cambio en el log para conservar historial.
        logger.info(f"Nombre actualizado para cliente {self.__id}: {self.__nombre}")

    @property
    def email(self) -> str:
        # Permitimos lectura controlada del correo.
        return self.__email

    @property
    def telefono(self) -> str:
        # Permitimos lectura controlada del teléfono.
        return self.__telefono

    @telefono.setter
    def telefono(self, nuevo_telefono: str) -> None:
        # Guardamos el teléfono limpio sin imponer validación rígida.
        self.__telefono = nuevo_telefono.strip()
        # Registramos el cambio para mantener trazabilidad.
        logger.info(f"Telefono actualizado para cliente {self.__id}: {self.__telefono}")

    @property
    def activo(self) -> bool:
        # Exponemos el estado activo del cliente en modo de solo lectura.
        return self.__activo

    def desactivar(self) -> None:
        # Marcamos al cliente como inactivo sin borrarlo del sistema.
        self.__activo = False
        # Registramos la baja lógica para auditoría.
        logger.advertencia(f"Cliente desactivado: {self.__nombre} | ID: {self.__id}")

    def activar(self) -> None:
        # Volvemos a habilitar al cliente para operaciones futuras.
        self.__activo = True
        # Registramos la reactivación para dejar historial.
        logger.info(f"Cliente reactivado: {self.__nombre} | ID: {self.__id}")


# Esta clase administra la colección de clientes registrados.
class GestorClientes:
    """Gestor en memoria para crear, buscar y listar clientes."""

    def __init__(self):
        # Inicializamos una lista privada donde se guardarán los clientes.
        self.__clientes: list[Cliente] = []

    def registrar_cliente(
        self, numero_id: str, nombre: str, email: str, telefono: str = ""
    ) -> Cliente:
        # Verificamos si ya existe un cliente con la misma identificación.
        if self.__id_existe(numero_id):
            raise ErrorClienteYaExiste(f"identificacion {numero_id.strip()}")
        # Verificamos si ya existe un cliente con el mismo correo.
        if self.__email_existe(email):
            raise ErrorClienteYaExiste(email.strip().lower())
        # Creamos el objeto cliente cuando las validaciones previas pasan.
        nuevo_cliente = Cliente(numero_id, nombre, email, telefono)
        # Guardamos el cliente dentro de la lista administrada por el gestor.
        self.__clientes.append(nuevo_cliente)
        # Devolvemos el objeto recién creado para seguir trabajando con él.
        return nuevo_cliente

    def buscar_por_email(self, email: str) -> Cliente:
        # Normalizamos el correo para comparar sin diferencias de mayúsculas.
        email_normalizado = email.strip().lower()
        # Recorremos todos los clientes registrados.
        for cliente in self.__clientes:
            # Retornamos el cliente apenas encontramos coincidencia.
            if cliente.email == email_normalizado:
                return cliente
        # Si no hubo coincidencia, informamos el error con una excepción clara.
        raise ErrorClienteNoEncontrado(email)

    def buscar_por_id(self, numero_id: str) -> Cliente:
        # Normalizamos la identificación para evitar errores por espacios.
        identificacion = numero_id.strip()
        # Recorremos la lista interna hasta encontrar un ID igual.
        for cliente in self.__clientes:
            # Comparamos la identificación del objeto actual con la buscada.
            if cliente.obtener_id() == identificacion:
                return cliente
        # Si no se encontró ningún cliente, lanzamos la excepción de negocio.
        raise ErrorClienteNoEncontrado(numero_id)

    def listar_clientes(self) -> list[Cliente]:
        # Devolvemos una copia para proteger la lista interna del gestor.
        return list(self.__clientes)

    def total_clientes(self) -> int:
        # Retornamos el tamaño actual de la colección administrada.
        return len(self.__clientes)

    def __email_existe(self, email: str) -> bool:
        # Normalizamos el correo recibido para compararlo correctamente.
        email_normalizado = email.strip().lower()
        # Verificamos si al menos un cliente tiene ese mismo correo.
        return any(cliente.email == email_normalizado for cliente in self.__clientes)

    def __id_existe(self, numero_id: str) -> bool:
        # Normalizamos la identificación antes de buscar duplicados.
        identificacion = numero_id.strip()
        # Verificamos si al menos un cliente ya usa esa identificación.
        return any(cliente.obtener_id() == identificacion for cliente in self.__clientes)

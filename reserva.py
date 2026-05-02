"""
reserva.py
Autor: Jesús David Rodríguez Alvarado
Curso: Programación 213023 - UNAD
==========
Define la clase Reserva y el gestor encargado de administrarlas.
La reserva conecta clientes, servicios, tiempo y estados del flujo.
"""

# Importamos datetime para sellar la fecha de creación de cada reserva.
from datetime import datetime
# Importamos uuid para generar un identificador único por reserva.
import uuid

# Importamos el modelo Cliente para tipado y validaciones.
from cliente import Cliente
# Importamos el modelo Servicio para tipado y cálculos polimórficos.
from servicio import Servicio
# Importamos las excepciones de negocio que puede disparar este módulo.
from excepciones import (
    ErrorCalculoCosto,
    ErrorClienteInactivo,
    ErrorReservaCancelada,
    ErrorReservaDuracionInvalida,
    ErrorReservaEstadoInvalido,
    ErrorReservaNoEncontrada,
    ErrorReservaYaConfirmada,
)
# Importamos el logger del proyecto para registrar eventos del flujo.
import logger


# Este estado representa una reserva recién creada y aún no confirmada.
ESTADO_PENDIENTE = "PENDIENTE"
# Este estado representa una reserva ya confirmada con costo calculado.
ESTADO_CONFIRMADA = "CONFIRMADA"
# Este estado representa una reserva anulada antes de completarse.
ESTADO_CANCELADA = "CANCELADA"
# Este estado representa una reserva que ya fue atendida y cerrada.
ESTADO_PROCESADA = "PROCESADA"


# Esta clase modela una reserva individual dentro del sistema.
class Reserva:
    """Representa una reserva de un cliente sobre un servicio."""

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float):
        # Rechazamos duraciones nulas o negativas desde el inicio.
        if horas <= 0:
            raise ErrorReservaDuracionInvalida(horas)
        # Rechazamos clientes inactivos para impedir reservas inválidas.
        if not cliente.activo:
            raise ErrorClienteInactivo(cliente.obtener_id())
        # Verificamos que el servicio esté activo antes de apartarlo.
        servicio.verificar_disponibilidad()
        # Generamos un identificador corto y fácil de leer.
        self.__id = uuid.uuid4().hex[:10].upper()
        # Guardamos la referencia al cliente que realiza la reserva.
        self.__cliente = cliente
        # Guardamos la referencia al servicio reservado.
        self.__servicio = servicio
        # Guardamos la duración solicitada.
        self.__horas = float(horas)
        # La reserva inicia siempre en estado pendiente.
        self.__estado = ESTADO_PENDIENTE
        # Registramos la fecha exacta de creación.
        self.__fecha_creacion = datetime.now()
        # El costo queda sin calcular hasta la confirmación.
        self.__costo_calculado: float | None = None
        # Registramos la creación para trazabilidad del proceso.
        logger.info(
            f"Reserva creada | ID: {self.__id} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | Horas: {self.__horas} | Estado: {self.__estado}"
        )

    def __validar_estado_para_confirmar(self) -> None:
        # Si la reserva ya estaba confirmada, no tiene sentido repetir la acción.
        if self.__estado == ESTADO_CONFIRMADA:
            raise ErrorReservaYaConfirmada(self.__id)
        # Si la reserva fue cancelada, no puede volver a confirmarse.
        if self.__estado == ESTADO_CANCELADA:
            raise ErrorReservaCancelada(self.__id)
        # Si la reserva ya se procesó, tampoco puede regresar al flujo anterior.
        if self.__estado == ESTADO_PROCESADA:
            raise ErrorReservaEstadoInvalido(self.__id, self.__estado, "confirmar")

    def confirmar(self, **kwargs_costo) -> float:
        # Validamos primero si el estado permite una confirmación.
        self.__validar_estado_para_confirmar()
        try:
            # Calculamos el costo final delegando en el servicio correspondiente.
            self.__costo_calculado = self.__servicio.calcular_costo(
                self.__horas,
                **kwargs_costo,
            )
            # Actualizamos el estado solo después de un cálculo exitoso.
            self.__estado = ESTADO_CONFIRMADA
            # Registramos la confirmación con el valor calculado.
            logger.info(
                f"Reserva confirmada | ID: {self.__id} | Costo: ${self.__costo_calculado:,.2f}"
            )
            # Devolvemos el costo final al llamador.
            return self.__costo_calculado
        except ErrorCalculoCosto:
            # Registramos el fallo sin alterar el tipo original del error.
            logger.error(f"Error al calcular costo en reserva {self.__id}.")
            # Reenviamos la excepción para que la maneje la capa superior.
            raise
        finally:
            # Dejamos registro de que el intento de confirmación terminó.
            logger.info(f"Intento de confirmacion finalizado para reserva {self.__id}")

    def cancelar(self, motivo: str = "Sin especificar") -> None:
        # Si ya estaba cancelada, evitamos una segunda cancelación.
        if self.__estado == ESTADO_CANCELADA:
            raise ErrorReservaCancelada(self.__id)
        # Si ya fue procesada, tampoco puede cancelarse a posteriori.
        if self.__estado == ESTADO_PROCESADA:
            raise ErrorReservaEstadoInvalido(self.__id, self.__estado, "cancelar")
        # Normalizamos el motivo para no dejar textos vacíos.
        motivo_limpio = motivo.strip() or "Sin especificar"
        # Cambiamos el estado a cancelada.
        self.__estado = ESTADO_CANCELADA
        # Registramos la cancelación junto con su motivo.
        logger.advertencia(
            f"Reserva cancelada | ID: {self.__id} | Cliente: {self.__cliente.nombre} | Motivo: {motivo_limpio}"
        )

    def procesar(self) -> str:
        # Si la reserva está cancelada, no puede entregarse ni cobrarse.
        if self.__estado == ESTADO_CANCELADA:
            raise ErrorReservaCancelada(self.__id)
        # Si la reserva no está confirmada, el flujo todavía no está completo.
        if self.__estado != ESTADO_CONFIRMADA:
            raise ErrorReservaEstadoInvalido(self.__id, self.__estado, "procesar")
        # Cambiamos el estado para reflejar que la reserva fue completada.
        self.__estado = ESTADO_PROCESADA
        # Construimos el resumen que verá el usuario en consola.
        resumen = (
            "RESERVA PROCESADA\n"
            f"  ID Reserva : {self.__id}\n"
            f"  Cliente    : {self.__cliente.nombre}\n"
            f"  Servicio   : {self.__servicio.nombre}\n"
            f"  Horas      : {self.__horas}\n"
            f"  Costo total: ${self.__costo_calculado:,.2f}\n"
            f"  Estado     : {self.__estado}"
        )
        # Registramos la finalización del servicio.
        logger.info(
            f"Reserva procesada | ID: {self.__id} | Costo: ${self.__costo_calculado:,.2f}"
        )
        # Devolvemos el resumen listo para mostrar.
        return resumen

    @property
    def id_reserva(self) -> str:
        # Exponemos el identificador único de la reserva.
        return self.__id

    @property
    def estado(self) -> str:
        # Exponemos el estado actual de la reserva.
        return self.__estado

    @property
    def cliente(self) -> Cliente:
        # Exponemos el cliente asociado a la reserva.
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        # Exponemos el servicio asociado a la reserva.
        return self.__servicio

    @property
    def horas(self) -> float:
        # Exponemos la duración solicitada para la reserva.
        return self.__horas

    @property
    def costo(self) -> float | None:
        # Exponemos el costo ya calculado o None si aún no existe.
        return self.__costo_calculado

    @property
    def fecha_creacion(self) -> datetime:
        # Exponemos la marca de tiempo de creación.
        return self.__fecha_creacion

    def describir(self) -> str:
        # Formateamos el costo según ya exista o siga pendiente.
        costo_str = (
            f"${self.__costo_calculado:,.2f}"
            if self.__costo_calculado is not None
            else "Por calcular"
        )
        # Construimos una descripción completa y legible.
        return (
            f"Reserva [{self.__id}]\n"
            f"  Cliente    : {self.__cliente.nombre} ({self.__cliente.email})\n"
            f"  Servicio   : {self.__servicio.nombre}\n"
            f"  Duracion   : {self.__horas} horas\n"
            f"  Costo      : {costo_str}\n"
            f"  Estado     : {self.__estado}\n"
            f"  Creada     : {self.__fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __str__(self) -> str:
        # Devolvemos una representación breve útil en listados y depuración.
        return (
            f"Reserva[{self.__id}] - {self.__cliente.nombre} - "
            f"{self.__servicio.nombre} - {self.__estado}"
        )


# Esta clase administra la colección completa de reservas del sistema.
class GestorReservas:
    """Gestor en memoria para crear, buscar y listar reservas."""

    def __init__(self):
        # Inicializamos una lista privada para almacenar las reservas.
        self.__reservas: list[Reserva] = []

    def crear_reserva(self, cliente: Cliente, servicio: Servicio, horas: float) -> Reserva:
        # Creamos la reserva delegando validaciones a la propia clase Reserva.
        nueva_reserva = Reserva(cliente, servicio, horas)
        # Agregamos la nueva reserva a la lista administrada.
        self.__reservas.append(nueva_reserva)
        # Retornamos la reserva creada para seguir operando con ella.
        return nueva_reserva

    def buscar_por_id(self, id_reserva: str) -> Reserva:
        # Normalizamos el ID recibido para compararlo en mayúsculas.
        identificador = id_reserva.strip().upper()
        # Recorremos la colección interna de reservas.
        for reserva in self.__reservas:
            # Devolvemos la reserva apenas encontramos coincidencia.
            if reserva.id_reserva == identificador:
                return reserva
        # Si no hubo coincidencia, notificamos con una excepción de dominio.
        raise ErrorReservaNoEncontrada(id_reserva)

    def listar_por_cliente(self, email_cliente: str) -> list[Reserva]:
        # Normalizamos el email del cliente para comparar de forma consistente.
        email_normalizado = email_cliente.strip().lower()
        # Filtramos y devolvemos solo las reservas del email indicado.
        return [
            reserva
            for reserva in self.__reservas
            if reserva.cliente.email == email_normalizado
        ]

    def listar_por_estado(self, estado: str) -> list[Reserva]:
        # Normalizamos el estado solicitado en mayúsculas.
        estado_normalizado = estado.strip().upper()
        # Filtramos las reservas que coinciden con ese estado.
        return [
            reserva
            for reserva in self.__reservas
            if reserva.estado == estado_normalizado
        ]

    def listar_todas(self) -> list[Reserva]:
        # Devolvemos una copia para no exponer la lista interna real.
        return list(self.__reservas)

    def total_reservas(self) -> int:
        # Retornamos cuántas reservas existen actualmente.
        return len(self.__reservas)

    def ingresos_totales(self) -> float:
        # Sumamos solo las reservas procesadas que sí tienen costo calculado.
        return sum(
            reserva.costo
            for reserva in self.__reservas
            if reserva.estado == ESTADO_PROCESADA and reserva.costo is not None
        )
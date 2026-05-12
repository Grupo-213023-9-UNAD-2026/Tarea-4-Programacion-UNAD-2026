"""
excepciones.py
Autor: Paula Nikoll Arteta Guillen
Curso: Programación 213023 - UNAD
==============
Define las excepciones personalizadas del proyecto Software FJ.

El objetivo de este archivo es centralizar los errores del dominio
para que el resto del sistema capture mensajes consistentes y claros.
"""


# La clase base agrupa todos los errores propios del sistema.
class ErrorSistema(Exception):
    """Clase base para cualquier error controlado del proyecto."""

    def __init__(self, mensaje: str, codigo: int = 0):
        # Guardamos el mensaje para reutilizarlo en consola y en pruebas.
        self.mensaje = mensaje
        # Guardamos un código numérico para facilitar la identificación.
        self.codigo = codigo
        # Inicializamos la clase padre con el mismo mensaje descriptivo.
        super().__init__(mensaje)

    def __str__(self) -> str:
        # Mostramos el código junto con el mensaje para que el error sea más útil.
        return f"[Error {self.codigo}] {self.mensaje}"


# Esta clase agrupa todos los errores relacionados con clientes.
class ErrorCliente(ErrorSistema):
    """Clase base para errores de clientes."""


# Este error se usa cuando la identificación del cliente es inválida.
class ErrorClienteIdentificacionInvalida(ErrorCliente):
    """Se lanza cuando la identificación del cliente no cumple lo esperado."""

    def __init__(self, identificacion: str):
        # Construimos un mensaje claro con el dato recibido.
        super().__init__(
            f"La identificación '{identificacion}' es inválida. "
            "Debe contener información y no puede quedar vacía.",
            codigo=100,
        )


# Este error se usa cuando el nombre no cumple el formato permitido.
class ErrorClienteNombreInvalido(ErrorCliente):
    """Se lanza cuando el nombre del cliente es inválido."""

    def __init__(self, nombre_recibido: str):
        # Indicamos el valor problemático para facilitar la depuración.
        super().__init__(
            f"El nombre de cliente '{nombre_recibido}' es inválido. "
            "Debe contener solo letras y espacios, y no puede estar vacío.",
            codigo=101,
        )


# Este error se usa cuando el correo no tiene el formato esperado.
class ErrorClienteEmailInvalido(ErrorCliente):
    """Se lanza cuando el email del cliente no es válido."""

    def __init__(self, email_recibido: str):
        # Explicamos el formato esperado para orientar la corrección.
        super().__init__(
            f"El email '{email_recibido}' no tiene un formato válido. "
            "Debe contener '@' y un dominio, por ejemplo usuario@correo.com.",
            codigo=102,
        )


# Este error se usa cuando un dato único ya existe en el sistema.
class ErrorClienteYaExiste(ErrorCliente):
    """Se lanza cuando se intenta duplicar un cliente."""

    def __init__(self, dato_duplicado: str):
        # El mensaje deja claro qué dato causó el conflicto.
        super().__init__(
            f"Ya existe un cliente registrado con el dato '{dato_duplicado}'.",
            codigo=103,
        )


# Este error se usa cuando no aparece el cliente buscado.
class ErrorClienteNoEncontrado(ErrorCliente):
    """Se lanza cuando no se encuentra un cliente solicitado."""

    def __init__(self, identificador: str):
        # El mensaje incluye el criterio de búsqueda usado por el usuario.
        super().__init__(
            f"No se encontró ningún cliente con el identificador '{identificador}'.",
            codigo=104,
        )


# Este error se usa cuando un cliente existe pero está inactivo.
class ErrorClienteInactivo(ErrorCliente):
    """Se lanza cuando se intenta operar con un cliente desactivado."""

    def __init__(self, identificador: str):
        # El mensaje explica por qué la operación no puede continuar.
        super().__init__(
            f"El cliente '{identificador}' está inactivo y no puede usar esta operación.",
            codigo=105,
        )


# Esta clase agrupa todos los errores relacionados con servicios.
class ErrorServicio(ErrorSistema):
    """Clase base para errores de servicios."""


# Este error se usa cuando un servicio no está disponible para reservar.
class ErrorServicioNoDisponible(ErrorServicio):
    """Se lanza cuando el servicio existe, pero está desactivado."""

    def __init__(self, nombre_servicio: str):
        # El mensaje describe el servicio que no pudo ser usado.
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible en este momento.",
            codigo=201,
        )


# Este error se usa cuando un parámetro del servicio tiene un valor inválido.
class ErrorServicioParametroInvalido(ErrorServicio):
    """Se lanza cuando un parámetro del servicio no pasa la validación."""

    def __init__(self, parametro: str, valor_recibido, descripcion: str = ""):
        # Concatenamos una descripción extra solo si realmente se suministró.
        detalle = f" {descripcion}" if descripcion else ""
        # El mensaje muestra el parámetro y el valor recibido.
        super().__init__(
            f"El parámetro '{parametro}' tiene un valor inválido: '{valor_recibido}'.{detalle}",
            codigo=202,
        )


# Este error se usa cuando se intenta crear un tipo de servicio no contemplado.
class ErrorServicioTipoDesconocido(ErrorServicio):
    """Se lanza cuando el tipo de servicio no existe en el catálogo esperado."""

    def __init__(self, tipo: str):
        # El mensaje incluye los tipos válidos definidos en el proyecto.
        super().__init__(
            f"El tipo de servicio '{tipo}' no es reconocido por el sistema. "
            "Tipos válidos: SalaReuniones, AlquilerEquipo, AsesoriaTecnica.",
            codigo=203,
        )


# Este error se usa cuando no se encuentra un servicio por ID.
class ErrorServicioNoEncontrado(ErrorServicio):
    """Se lanza cuando un servicio no existe en el catálogo."""

    def __init__(self, identificador: str):
        # El mensaje deja claro que el problema es de búsqueda, no de disponibilidad.
        super().__init__(
            f"No se encontró ningún servicio con el identificador '{identificador}'.",
            codigo=204,
        )


# Esta clase agrupa todos los errores relacionados con reservas.
class ErrorReserva(ErrorSistema):
    """Clase base para errores de reservas."""


# Este error se usa cuando se intenta confirmar una reserva ya confirmada.
class ErrorReservaYaConfirmada(ErrorReserva):
    """Se lanza cuando una reserva ya pasó por confirmación."""

    def __init__(self, id_reserva: str):
        # El mensaje identifica la reserva afectada.
        super().__init__(
            f"La reserva '{id_reserva}' ya fue confirmada anteriormente.",
            codigo=301,
        )


# Este error se usa cuando una reserva cancelada recibe una nueva operación.
class ErrorReservaCancelada(ErrorReserva):
    """Se lanza cuando se intenta operar sobre una reserva cancelada."""

    def __init__(self, id_reserva: str):
        # El mensaje indica que la reserva ya no es modificable.
        super().__init__(
            f"La reserva '{id_reserva}' está cancelada y no puede modificarse.",
            codigo=302,
        )


# Este error se usa cuando la duración no es positiva.
class ErrorReservaDuracionInvalida(ErrorReserva):
    """Se lanza cuando la duración de la reserva es inválida."""

    def __init__(self, duracion: float):
        # El mensaje indica el valor problemático y la regla esperada.
        super().__init__(
            f"La duración '{duracion}' horas no es válida. "
            "Debe ser un número positivo mayor a 0.",
            codigo=303,
        )


# Este error se usa cuando una reserva no aparece en el gestor.
class ErrorReservaNoEncontrada(ErrorReserva):
    """Se lanza cuando no existe la reserva buscada."""

    def __init__(self, id_reserva: str):
        # El mensaje conserva el ID consultado para facilitar el rastreo.
        super().__init__(
            f"No se encontró ninguna reserva con el ID '{id_reserva}'.",
            codigo=304,
        )


# Este error se usa cuando una operación no encaja con el estado actual.
class ErrorReservaEstadoInvalido(ErrorReserva):
    """Se lanza cuando el estado de la reserva no permite la operación solicitada."""

    def __init__(self, id_reserva: str, estado_actual: str, operacion: str):
        # El mensaje deja claro qué operación se bloqueó y por qué.
        super().__init__(
            f"No se puede {operacion} la reserva '{id_reserva}' porque su estado actual es '{estado_actual}'.",
            codigo=305,
        )


# Este error se usa cuando falla un cálculo económico.
class ErrorCalculoCosto(ErrorSistema):
    """Se lanza cuando ocurre un error en el cálculo del costo."""

    def __init__(self, detalle: str):
        # El mensaje final se deja listo para mostrar sin más procesamiento.
        super().__init__(f"Error al calcular el costo: {detalle}", codigo=401)

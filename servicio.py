"""
servicio.py
Autor: Valery Donado Escalante
Curso: Programación 213023 - UNAD
===========
Define la jerarquía de servicios del sistema y el gestor que los
administra dentro del catálogo en memoria.
"""

# Importamos uuid para construir identificadores breves y únicos.
import uuid
# Importamos utilidades para crear la clase abstracta base del catálogo.
from abc import ABC, abstractmethod

# Importamos las excepciones del dominio de servicios y cálculos.
from excepciones import (
    ErrorCalculoCosto,
    ErrorServicioNoDisponible,
    ErrorServicioNoEncontrado,
    ErrorServicioParametroInvalido,
)
# Importamos el logger del proyecto para registrar eventos importantes.
import logger


# Esta clase abstracta define el contrato común de cualquier servicio.
class Servicio(ABC):
    """Clase base para servicios ofrecidos por el sistema."""

    def __init__(self, nombre: str, precio_hora: float, disponible: bool = True):
        # Rechazamos nombres vacíos para no crear servicios ambiguos.
        if not nombre or not nombre.strip():
            raise ErrorServicioParametroInvalido(
                "nombre",
                nombre,
                "El nombre del servicio no puede estar vacio.",
            )
        # Rechazamos precios menores o iguales a cero.
        if precio_hora <= 0:
            raise ErrorServicioParametroInvalido(
                "precio_hora",
                precio_hora,
                "El precio por hora debe ser mayor a 0.",
            )
        # Generamos un identificador corto y legible para el servicio.
        self._id = uuid.uuid4().hex[:8].upper()
        # Guardamos el nombre limpio del servicio.
        self._nombre = nombre.strip()
        # Guardamos el precio base por hora.
        self._precio_hora = float(precio_hora)
        # Guardamos el estado de disponibilidad actual.
        self._disponible = bool(disponible)
        # Registramos la creación del servicio para auditoría.
        logger.info(
            f"Servicio creado: {self._nombre} | Precio/h: ${self._precio_hora:.2f} | ID: {self._id}"
        )

    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        # Cada subclase debe definir su propia forma de calcular el costo.
        raise NotImplementedError

    @abstractmethod
    def describir(self) -> str:
        # Cada subclase debe devolver una descripción detallada.
        raise NotImplementedError

    @abstractmethod
    def validar_parametros(self, horas: float) -> bool:
        # Cada subclase debe validar las reglas específicas de reserva.
        raise NotImplementedError

    def obtener_id(self) -> str:
        # Exponemos el identificador único del servicio.
        return self._id

    def esta_disponible(self) -> bool:
        # Retornamos si el servicio puede reservarse en este momento.
        return self._disponible

    def activar(self) -> None:
        # Marcamos el servicio como disponible nuevamente.
        self._disponible = True
        # Registramos la activación para dejar trazabilidad.
        logger.info(f"Servicio activado: {self._nombre}")

    def desactivar(self) -> None:
        # Marcamos el servicio como no disponible para nuevas reservas.
        self._disponible = False
        # Registramos la desactivación en el historial del sistema.
        logger.advertencia(f"Servicio desactivado: {self._nombre}")

    def verificar_disponibilidad(self) -> None:
        # Si el servicio está desactivado, detenemos la operación con un error claro.
        if not self._disponible:
            raise ErrorServicioNoDisponible(self._nombre)

    @property
    def nombre(self) -> str:
        # Permitimos lectura controlada del nombre.
        return self._nombre

    @property
    def precio_hora(self) -> float:
        # Permitimos lectura controlada del precio base.
        return self._precio_hora

    def __str__(self) -> str:
        # Construimos una representación corta y útil para listados rápidos.
        return f"{self._nombre} (ID: {self._id}) - ${self._precio_hora:.2f}/h"


# Esta subclase representa el alquiler de una sala de reuniones.
class SalaReuniones(Servicio):
    """Servicio para reservar salas por hora."""

    # Definimos la duración mínima permitida para este servicio.
    HORAS_MINIMAS = 1.0
    # Definimos el recargo fijo para salas grandes.
    CARGO_SALA_GRANDE = 50000

    def __init__(self, nombre: str, precio_hora: float, capacidad: int):
        # Inicializamos la parte común del servicio.
        super().__init__(nombre, precio_hora)
        # Rechazamos capacidades no positivas.
        if capacidad <= 0:
            raise ErrorServicioParametroInvalido(
                "capacidad",
                capacidad,
                "La capacidad debe ser al menos 1 persona.",
            )
        # Guardamos la capacidad propia de la sala.
        self.__capacidad = int(capacidad)

    def calcular_costo(self, horas: float, aplicar_iva: bool = True) -> float:
        # Encerramos el cálculo para convertir errores técnicos en errores de dominio.
        try:
            # Validamos las horas antes de iniciar el cálculo.
            self.validar_parametros(horas)
            # Calculamos el costo base multiplicando horas por tarifa.
            costo_base = float(horas) * self._precio_hora
            # Definimos si la sala aplica o no el recargo por tamaño.
            cargo_extra = self.CARGO_SALA_GRANDE if self.__capacidad > 10 else 0
            # Sumamos el costo base con el recargo fijo.
            subtotal = costo_base + cargo_extra
            # Calculamos el IVA únicamente si el usuario lo solicitó.
            iva = subtotal * 0.19 if aplicar_iva else 0
            # Sumamos el subtotal más el impuesto si corresponde.
            total = subtotal + iva
            # Redondeamos el resultado final para presentación monetaria.
            return round(total, 2)
        except ErrorServicioParametroInvalido:
            # Reenviamos intacto cualquier error de validación de negocio.
            raise
        except (TypeError, ValueError) as error:
            # Envolvemos errores de tipo o conversión en un error de cálculo propio.
            raise ErrorCalculoCosto(f"SalaReuniones: {error}") from error

    def describir(self) -> str:
        # Traducimos la regla de sala grande a una etiqueta más fácil de leer.
        grande = "Si" if self.__capacidad > 10 else "No"
        # Devolvemos una descripción completa del servicio.
        return (
            f"Sala de Reuniones [{self._id}]\n"
            f"  Nombre         : {self._nombre}\n"
            f"  Precio/hora    : ${self._precio_hora:,.0f}\n"
            f"  Capacidad      : {self.__capacidad} personas\n"
            f"  Sala grande    : {grande} (cargo extra: ${self.CARGO_SALA_GRANDE:,})\n"
            f"  Disponible     : {'Si' if self._disponible else 'No'}"
        )

    def validar_parametros(self, horas: float) -> bool:
        # Rechazamos reservas de sala por debajo del mínimo establecido.
        if horas < self.HORAS_MINIMAS:
            raise ErrorServicioParametroInvalido(
                "horas",
                horas,
                f"La sala de reuniones requiere minimo {self.HORAS_MINIMAS} hora(s).",
            )
        # Retornamos True para dejar explícito que la validación fue exitosa.
        return True

    @property
    def capacidad(self) -> int:
        # Permitimos lectura controlada de la capacidad máxima.
        return self.__capacidad


# Esta subclase representa el alquiler temporal de equipos.
class AlquilerEquipo(Servicio):
    """Servicio para alquilar equipos tecnológicos por horas."""

    # Definimos el porcentaje de descuento por volumen.
    DESCUENTO_VOLUMEN = 0.10
    # Definimos la cantidad mínima necesaria para ese descuento.
    CANTIDAD_PARA_DESCUENTO = 3

    def __init__(self, nombre: str, precio_hora: float, tipo_equipo: str):
        # Inicializamos la parte común del servicio.
        super().__init__(nombre, precio_hora)
        # Rechazamos tipos vacíos porque impedirían describir bien el servicio.
        if not tipo_equipo or not tipo_equipo.strip():
            raise ErrorServicioParametroInvalido(
                "tipo_equipo",
                tipo_equipo,
                "El tipo de equipo no puede estar vacio.",
            )
        # Guardamos el tipo de equipo limpio para uso posterior.
        self.__tipo_equipo = tipo_equipo.strip()

    def calcular_costo(
        self, horas: float, cantidad: int = 1, con_descuento: bool = True
    ) -> float:
        # Encerramos el cálculo para ofrecer errores coherentes al usuario.
        try:
            # Validamos primero la duración solicitada.
            self.validar_parametros(horas)
            # Rechazamos cantidades menores o iguales a cero.
            if cantidad <= 0:
                raise ErrorServicioParametroInvalido(
                    "cantidad",
                    cantidad,
                    "La cantidad de equipos debe ser al menos 1.",
                )
            # Calculamos el costo unitario de un solo equipo.
            costo_unitario = float(horas) * self._precio_hora
            # Multiplicamos por la cantidad solicitada.
            costo_total = costo_unitario * int(cantidad)
            # Aplicamos el descuento únicamente si el volumen lo permite.
            if con_descuento and cantidad >= self.CANTIDAD_PARA_DESCUENTO:
                costo_total -= costo_total * self.DESCUENTO_VOLUMEN
            # Redondeamos el valor final para manejo monetario.
            return round(costo_total, 2)
        except ErrorServicioParametroInvalido:
            # Reenviamos los errores de negocio sin alterarlos.
            raise
        except (TypeError, ValueError) as error:
            # Convertimos errores técnicos en una excepción del dominio.
            raise ErrorCalculoCosto(f"AlquilerEquipo: {error}") from error

    def describir(self) -> str:
        # Devolvemos un resumen legible del servicio y su descuento.
        return (
            f"Alquiler de Equipo [{self._id}]\n"
            f"  Nombre      : {self._nombre}\n"
            f"  Tipo        : {self.__tipo_equipo}\n"
            f"  Precio/hora : ${self._precio_hora:,.0f}\n"
            f"  Desc. 3+    : {int(self.DESCUENTO_VOLUMEN * 100)}% al alquilar {self.CANTIDAD_PARA_DESCUENTO}+ equipos\n"
            f"  Disponible  : {'Si' if self._disponible else 'No'}"
        )

    def validar_parametros(self, horas: float) -> bool:
        # Rechazamos alquileres con duración nula o negativa.
        if horas <= 0:
            raise ErrorServicioParametroInvalido(
                "horas",
                horas,
                "La duracion del alquiler debe ser mayor a 0 horas.",
            )
        # Retornamos True para señalar éxito en la validación.
        return True

    @property
    def tipo_equipo(self) -> str:
        # Permitimos lectura controlada del tipo de equipo.
        return self.__tipo_equipo


# Esta subclase representa un servicio de asesoría especializada.
class AsesoriaTecnica(Servicio):
    """Servicio para asesorías técnicas con niveles de experiencia."""

    # Cada nivel modifica el costo base por hora del servicio.
    MULTIPLICADORES = {
        "junior": 1.0,
        "senior": 1.5,
        "experto": 2.0,
    }
    # Definimos la duración mínima permitida para asesorías.
    HORAS_MINIMAS = 0.5

    def __init__(self, nombre: str, precio_hora: float, especialidad: str, nivel: str = "junior"):
        # Inicializamos la parte común del servicio.
        super().__init__(nombre, precio_hora)
        # Rechazamos especialidades vacías porque el servicio perdería contexto.
        if not especialidad or not especialidad.strip():
            raise ErrorServicioParametroInvalido(
                "especialidad",
                especialidad,
                "La especialidad de la asesoria no puede estar vacia.",
            )
        # Normalizamos el nivel para compararlo de forma consistente.
        nivel_normalizado = nivel.strip().lower()
        # Rechazamos niveles que no pertenezcan al catálogo esperado.
        if nivel_normalizado not in self.MULTIPLICADORES:
            raise ErrorServicioParametroInvalido(
                "nivel",
                nivel,
                f"El nivel debe ser uno de: {', '.join(self.MULTIPLICADORES)}.",
            )
        # Guardamos la especialidad limpia.
        self.__especialidad = especialidad.strip()
        # Guardamos el nivel ya normalizado para cálculos posteriores.
        self.__nivel = nivel_normalizado

    def calcular_costo(self, horas: float, incluir_informe: bool = False) -> float:
        # Encerramos el cálculo para producir errores de negocio coherentes.
        try:
            # Validamos la duración antes de seguir.
            self.validar_parametros(horas)
            # Buscamos el multiplicador asociado al nivel actual.
            multiplicador = self.MULTIPLICADORES[self.__nivel]
            # Calculamos el costo base aplicando horas, tarifa y nivel.
            costo_base = float(horas) * self._precio_hora * multiplicador
            # Calculamos el cargo adicional solo si se pidió informe.
            cargo_informe = costo_base * 0.15 if incluir_informe else 0
            # Sumamos el costo base más el valor adicional.
            total = costo_base + cargo_informe
            # Redondeamos el valor final a dos decimales.
            return round(total, 2)
        except ErrorServicioParametroInvalido:
            # Reenviamos validaciones fallidas sin envolverlas.
            raise
        except (TypeError, ValueError) as error:
            # Envolvemos cualquier fallo técnico como error de cálculo del dominio.
            raise ErrorCalculoCosto(f"AsesoriaTecnica: {error}") from error

    def describir(self) -> str:
        # Recuperamos el multiplicador solo para mostrarlo en la descripción.
        multiplicador = self.MULTIPLICADORES[self.__nivel]
        # Construimos una descripción detallada del servicio.
        return (
            f"Asesoria Tecnica [{self._id}]\n"
            f"  Nombre         : {self._nombre}\n"
            f"  Especialidad   : {self.__especialidad}\n"
            f"  Nivel asesor   : {self.__nivel.capitalize()} (x{multiplicador})\n"
            f"  Precio/hora    : ${self._precio_hora:,.0f}\n"
            f"  Disponible     : {'Si' if self._disponible else 'No'}"
        )

    def validar_parametros(self, horas: float) -> bool:
        # Rechazamos asesorías por debajo del mínimo admitido.
        if horas < self.HORAS_MINIMAS:
            raise ErrorServicioParametroInvalido(
                "horas",
                horas,
                f"La asesoria tecnica requiere minimo {self.HORAS_MINIMAS} horas.",
            )
        # Retornamos True para indicar validación exitosa.
        return True

    @property
    def especialidad(self) -> str:
        # Permitimos lectura controlada de la especialidad.
        return self.__especialidad

    @property
    def nivel(self) -> str:
        # Permitimos lectura controlada del nivel del asesor.
        return self.__nivel


# Esta clase administra la colección de servicios del sistema.
class GestorServicios:
    """Gestor en memoria para registrar y consultar servicios."""

    def __init__(self):
        # Inicializamos la lista privada que almacena el catálogo.
        self.__servicios: list[Servicio] = []

    def agregar_servicio(self, servicio: Servicio) -> None:
        # Validamos que el objeto recibido pertenezca a la jerarquía correcta.
        if not isinstance(servicio, Servicio):
            raise TypeError("Solo se pueden agregar instancias de Servicio o subclases.")
        # Guardamos el servicio dentro del catálogo administrado.
        self.__servicios.append(servicio)
        # Registramos la incorporación del servicio al catálogo.
        logger.info(f"Servicio agregado al catalogo: {servicio.nombre}")

    def buscar_por_id(self, id_servicio: str) -> Servicio:
        # Normalizamos el identificador para evitar fallos por formato.
        identificador = id_servicio.strip().upper()
        # Recorremos todos los servicios almacenados.
        for servicio in self.__servicios:
            # Retornamos el servicio apenas encontramos coincidencia.
            if servicio.obtener_id() == identificador:
                return servicio
        # Si no hay coincidencia, lanzamos el error correcto de búsqueda.
        raise ErrorServicioNoEncontrado(id_servicio)

    def listar_servicios(self, solo_disponibles: bool = False) -> list[Servicio]:
        # Si se pidieron solo disponibles, filtramos por estado activo.
        if solo_disponibles:
            return [servicio for servicio in self.__servicios if servicio.esta_disponible()]
        # En caso contrario devolvemos una copia del catálogo completo.
        return list(self.__servicios)

    def total_servicios(self) -> int:
        # Retornamos la cantidad actual de servicios registrados.
        return len(self.__servicios)

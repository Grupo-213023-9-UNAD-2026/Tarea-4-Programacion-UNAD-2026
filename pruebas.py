"""
pruebas.py
Autor: Jesús David Rodríguez Alvarado
Curso: Programación 213023 - UNAD
==========
Contiene una simulación completa del sistema con once operaciones.
Sirve para validar que clientes, servicios, reservas y logs funcionen
correctamente tanto de forma aislada como integrados entre sí.
"""

# Importamos el modelo Cliente y su gestor para las pruebas de clientes.
from cliente import Cliente, GestorClientes
# Importamos los tipos de servicio y el gestor del catálogo.
from servicio import AlquilerEquipo, AsesoriaTecnica, GestorServicios, SalaReuniones
# Importamos la reserva y su gestor para probar el flujo completo.
from reserva import GestorReservas, Reserva
# Importamos la excepción base del proyecto para capturar errores controlados.
from excepciones import ErrorSistema
# Importamos el logger para dejar registro del resultado de cada prueba.
import logger


# Esta clase agrupa ayudas visuales para hacer legible la simulación.
class UtilidadesPruebas:
    """Funciones auxiliares para mostrar separadores y resúmenes."""

    @staticmethod
    def separador(titulo: str) -> None:
        # Definimos una línea simple y compatible con cualquier consola.
        linea = "-" * 55
        # Imprimimos una separación visual antes de la prueba.
        print(f"\n{linea}")
        # Mostramos el título descriptivo de la prueba actual.
        print(f"  PRUEBA: {titulo}")
        # Cerramos el bloque con la misma línea.
        print(linea)

    @staticmethod
    def resumen_final(
        gestor_clientes: GestorClientes,
        gestor_servicios: GestorServicios,
        gestor_reservas: GestorReservas,
    ) -> None:
        # Definimos una línea destacada para el cierre de la simulación.
        linea = "=" * 55
        # Mostramos el bloque final con conteos e ingresos.
        print(f"\n{linea}")
        print("  RESUMEN FINAL DEL SISTEMA")
        print(linea)
        print(f"  Clientes registrados : {gestor_clientes.total_clientes()}")
        print(f"  Servicios en catalogo: {gestor_servicios.total_servicios()}")
        print(f"  Reservas totales     : {gestor_reservas.total_reservas()}")
        print(f"  Ingresos procesados  : ${gestor_reservas.ingresos_totales():,.2f} COP")
        print(linea)


# Esta clase reúne las pruebas asociadas al módulo de clientes.
class PruebasClientes:
    """Pruebas de registro y validación de clientes."""

    @staticmethod
    def prueba_cliente_valido(gestor: GestorClientes) -> Cliente | None:
        # Mostramos el separador para identificar el inicio de la prueba.
        UtilidadesPruebas.separador("01 - Registrar cliente valido")
        try:
            # Registramos un cliente con datos coherentes y completos.
            cliente = gestor.registrar_cliente(
                numero_id="1012345678",
                nombre="Carlos Andres Perez",
                email="carlos.perez@softwarefj.com",
                telefono="3001234567",
            )
            # Mostramos el cliente creado para ver el resultado.
            print(cliente.describir())
            # Registramos en el log que la prueba terminó correctamente.
            logger.info("PRUEBA 01 EXITOSA: Cliente valido registrado.")
            # Devolvemos el cliente para reutilizarlo en otras pruebas.
            return cliente
        except ErrorSistema as error:
            # Registramos el fallo en el archivo de log.
            logger.error(f"PRUEBA 01 fallo inesperadamente: {error}")
            # Devolvemos None para que el coordinador sepa que no puede reutilizarlo.
            return None

    @staticmethod
    def prueba_email_invalido(gestor: GestorClientes) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("02 - Cliente con email invalido")
        try:
            # Intentamos registrar un cliente con correo mal formado.
            gestor.registrar_cliente(
                numero_id="1098765432",
                nombre="Laura Gomez",
                email="lauragomez_sin_arroba",
            )
        except ErrorSistema as error:
            # Registramos que el error esperado fue manejado con éxito.
            logger.error(f"PRUEBA 02: Error esperado capturado -> {error}")
            # Mostramos al usuario que el sistema siguió estable.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si no hubo excepción, registramos una alerta grave en el log.
            logger.critico("PRUEBA 02: Se esperaba excepcion pero no ocurrio.")

    @staticmethod
    def prueba_nombre_invalido(gestor: GestorClientes) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("03 - Cliente con nombre invalido")
        try:
            # Intentamos registrar un cliente con números en el nombre.
            gestor.registrar_cliente(
                numero_id="1087654321",
                nombre="Juan123",
                email="juan@correo.com",
            )
        except ErrorSistema as error:
            # Registramos el error esperado en el log.
            logger.error(f"PRUEBA 03: Error esperado capturado -> {error}")
            # Mostramos el mensaje de control al usuario.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si el sistema aceptó el nombre inválido, lo señalamos como grave.
            logger.critico("PRUEBA 03: Se esperaba excepcion pero no ocurrio.")

    @staticmethod
    def prueba_cliente_duplicado(gestor: GestorClientes) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("04 - Cliente con dato duplicado")
        try:
            # Intentamos registrar un cliente con ID y correo ya existentes.
            gestor.registrar_cliente(
                numero_id="1012345678",
                nombre="Carlos Duplicado",
                email="carlos.perez@softwarefj.com",
            )
        except ErrorSistema as error:
            # Registramos el error esperado en el log.
            logger.error(f"PRUEBA 04: Error esperado capturado -> {error}")
            # Mostramos que el sistema manejó el duplicado sin caerse.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si el duplicado fue aceptado, lo registramos como un problema crítico.
            logger.critico("PRUEBA 04: Se esperaba excepcion por duplicado.")


# Esta clase reúne las pruebas asociadas al módulo de servicios.
class PruebasServicios:
    """Pruebas de creación y validación de servicios."""

    @staticmethod
    def prueba_servicios_validos(
        gestor_servicios: GestorServicios,
    ) -> tuple[SalaReuniones | None, AlquilerEquipo | None, AsesoriaTecnica | None]:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("05 - Crear servicios validos")
        try:
            # Creamos una sala de reuniones grande para probar el recargo.
            sala = SalaReuniones(
                nombre="Sala Bogota",
                precio_hora=80000,
                capacidad=15,
            )
            # Registramos la sala en el catálogo.
            gestor_servicios.agregar_servicio(sala)
            # Mostramos la descripción de la sala creada.
            print(sala.describir())

            # Creamos un servicio de alquiler de equipo para pruebas posteriores.
            equipo = AlquilerEquipo(
                nombre="Portatil HP ProBook",
                precio_hora=25000,
                tipo_equipo="Portatil",
            )
            # Registramos el equipo en el catálogo.
            gestor_servicios.agregar_servicio(equipo)
            # Mostramos la descripción del servicio creado.
            print(equipo.describir())

            # Creamos una asesoría técnica con nivel senior.
            asesoria = AsesoriaTecnica(
                nombre="Asesoria en Arquitectura de Software",
                precio_hora=120000,
                especialidad="Arquitectura de Software",
                nivel="senior",
            )
            # Registramos la asesoría en el catálogo.
            gestor_servicios.agregar_servicio(asesoria)
            # Mostramos la descripción del servicio creado.
            print(asesoria.describir())

            # Informamos en el log que la creación fue exitosa.
            logger.info("PRUEBA 05 EXITOSA: 3 servicios creados correctamente.")
            # Devolvemos los tres servicios para reutilizarlos.
            return sala, equipo, asesoria
        except ErrorSistema as error:
            # Registramos el fallo inesperado.
            logger.error(f"PRUEBA 05 fallo inesperadamente: {error}")
            # Devolvemos tuplas vacías para no romper el coordinador.
            return None, None, None

    @staticmethod
    def prueba_precio_invalido() -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("06 - Servicio con precio invalido")
        try:
            # Intentamos crear una sala con precio negativo.
            SalaReuniones(
                nombre="Sala Invalida",
                precio_hora=-5000,
                capacidad=5,
            )
        except ErrorSistema as error:
            # Registramos el error esperado en el log.
            logger.error(f"PRUEBA 06: Error esperado capturado -> {error}")
            # Confirmamos por consola que el sistema se mantuvo estable.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si no ocurrió la excepción esperada, dejamos constancia crítica.
            logger.critico("PRUEBA 06: Se esperaba excepcion por precio negativo.")


# Esta clase reúne las pruebas asociadas al módulo de reservas.
class PruebasReservas:
    """Pruebas del flujo de reservas y sus validaciones."""

    @staticmethod
    def prueba_reserva_exitosa(
        gestor_reservas: GestorReservas,
        cliente: Cliente,
        sala: SalaReuniones,
    ) -> Reserva | None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("07 - Reserva exitosa completa")
        try:
            # Creamos una reserva sobre una sala por tres horas.
            reserva = gestor_reservas.crear_reserva(cliente, sala, horas=3.0)
            # Mostramos el resumen corto de la reserva creada.
            print(f"  Reserva creada: {reserva}")
            # Confirmamos la reserva solicitando cálculo con IVA.
            costo = reserva.confirmar(aplicar_iva=True)
            # Mostramos el costo confirmado para verificar la operación.
            print(f"  Reserva confirmada. Costo total: ${costo:,.2f}")
            # Procesamos la reserva para cerrar el ciclo completo.
            resumen = reserva.procesar()
            # Mostramos el resumen final del procesamiento.
            print(resumen)
            # Registramos el éxito en el archivo de log.
            logger.info("PRUEBA 07 EXITOSA: Reserva procesada completamente.")
            # Devolvemos la reserva por si hiciera falta inspeccionarla.
            return reserva
        except ErrorSistema as error:
            # Registramos el fallo inesperado.
            logger.error(f"PRUEBA 07 fallo inesperadamente: {error}")
            # Devolvemos None para señalar que la prueba no produjo reserva usable.
            return None

    @staticmethod
    def prueba_duracion_invalida(
        gestor_reservas: GestorReservas,
        cliente: Cliente,
        equipo: AlquilerEquipo,
    ) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("08 - Reserva con duracion 0 horas")
        try:
            # Intentamos crear una reserva con duración inválida.
            gestor_reservas.crear_reserva(cliente, equipo, horas=0)
        except ErrorSistema as error:
            # Registramos el error esperado.
            logger.error(f"PRUEBA 08: Error esperado capturado -> {error}")
            # Mostramos el resultado controlado al usuario.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si no falló, registramos el problema como grave.
            logger.critico("PRUEBA 08: Se esperaba excepcion por duracion 0.")

    @staticmethod
    def prueba_confirmar_dos_veces(
        gestor_reservas: GestorReservas,
        cliente: Cliente,
        equipo: AlquilerEquipo,
    ) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("09 - Confirmar reserva ya confirmada")
        # Inicializamos la variable para poder revisarla en finally.
        reserva = None
        try:
            # Creamos una reserva nueva sobre el servicio de equipos.
            reserva = gestor_reservas.crear_reserva(cliente, equipo, horas=2.0)
            # Ejecutamos una primera confirmación válida.
            costo = reserva.confirmar(cantidad=1)
            # Mostramos el costo resultante de la primera confirmación.
            print(f"  Primera confirmacion exitosa. Costo: ${costo:,.2f}")
            # Intentamos confirmar la misma reserva por segunda vez.
            reserva.confirmar(cantidad=1)
        except ErrorSistema as error:
            # Registramos que el error esperado sí apareció.
            logger.error(f"PRUEBA 09: Error esperado capturado -> {error}")
            # Mostramos el resultado manejado en consola.
            print(f"  Sistema estable. Error manejado: {error}")
        else:
            # Si no hubo error, la validación del estado falló.
            logger.critico("PRUEBA 09: Se esperaba excepcion en segunda confirmacion.")
        finally:
            # Si la reserva existe, mostramos el estado final alcanzado.
            if reserva is not None:
                print(f"  Estado final de la reserva: {reserva.estado}")
            # Dejamos registro de que el bloque finally sí se ejecutó.
            logger.info("PRUEBA 09: Bloque finally ejecutado correctamente.")

    @staticmethod
    def prueba_servicio_no_disponible(
        gestor_reservas: GestorReservas,
        cliente: Cliente,
        asesoria: AsesoriaTecnica,
    ) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("10 - Reservar servicio desactivado")
        try:
            # Desactivamos el servicio para simular indisponibilidad.
            asesoria.desactivar()
            # Informamos al usuario sobre el cambio de estado.
            print(f"  Servicio '{asesoria.nombre}' desactivado.")
            # Intentamos crear una reserva con el servicio ya desactivado.
            gestor_reservas.crear_reserva(cliente, asesoria, horas=1.5)
        except ErrorSistema as error:
            # Registramos el error esperado.
            logger.error(f"PRUEBA 10: Error esperado capturado -> {error}")
            # Mostramos que el sistema siguió estable.
            print(f"  Sistema estable. Error manejado: {error}")
            # Reactivamos el servicio para no afectar otras pruebas.
            asesoria.activar()
            # Informamos al usuario que el servicio quedó disponible otra vez.
            print(f"  Servicio '{asesoria.nombre}' reactivado.")
        else:
            # Si no hubo error, la validación de disponibilidad falló.
            logger.critico("PRUEBA 10: Se esperaba excepcion por servicio no disponible.")
        finally:
            # Dejamos constancia de que el cierre de limpieza se ejecutó.
            logger.info("PRUEBA 10: Bloque finally ejecutado.")

    @staticmethod
    def prueba_descuento_por_volumen(
        gestor_clientes: GestorClientes,
        gestor_reservas: GestorReservas,
        equipo: AlquilerEquipo,
    ) -> None:
        # Mostramos el separador de la prueba actual.
        UtilidadesPruebas.separador("11 - Descuento por volumen")
        try:
            # Registramos un segundo cliente para esta prueba adicional.
            cliente_extra = gestor_clientes.registrar_cliente(
                numero_id="1076543210",
                nombre="Maria Fernanda Torres",
                email="mftorres@empresa.co",
                telefono="3152223344",
            )
            # Creamos una reserva nueva sobre el servicio de equipos.
            reserva = gestor_reservas.crear_reserva(cliente_extra, equipo, horas=3.0)
            # Confirmamos la reserva pidiendo cuatro equipos con descuento.
            costo_con_descuento = reserva.confirmar(cantidad=4, con_descuento=True)
            # Calculamos el mismo caso sin descuento para comparar.
            costo_sin_descuento = equipo.calcular_costo(
                3.0,
                cantidad=4,
                con_descuento=False,
            )
            # Mostramos el costo sin descuento.
            print(f"  Costo SIN descuento : ${costo_sin_descuento:,.2f}")
            # Mostramos el costo con descuento aplicado.
            print(f"  Costo CON descuento : ${costo_con_descuento:,.2f}")
            # Mostramos el ahorro obtenido.
            print(
                f"  Ahorro (10%)        : "
                f"${costo_sin_descuento - costo_con_descuento:,.2f}"
            )
            # Registramos en el log que el cálculo fue correcto.
            logger.info("PRUEBA 11 EXITOSA: Descuento por volumen aplicado correctamente.")
        except ErrorSistema as error:
            # Registramos cualquier fallo inesperado de la prueba.
            logger.error(f"PRUEBA 11 fallo inesperadamente: {error}")


# Esta clase coordina la ejecución ordenada de todas las pruebas.
class Simulador:
    """Orquesta la simulación completa del sistema."""

    def __init__(self):
        # Creamos un gestor vacío para los clientes de la simulación.
        self._gestor_clientes = GestorClientes()
        # Creamos un gestor vacío para el catálogo de servicios.
        self._gestor_servicios = GestorServicios()
        # Creamos un gestor vacío para las reservas de la simulación.
        self._gestor_reservas = GestorReservas()

    def ejecutar(self) -> None:
        # Marcamos el inicio de la simulación en el archivo de log.
        logger.iniciar_sesion()
        # Informamos al usuario que las pruebas están comenzando.
        print("  Iniciando simulacion automatica...")

        # Ejecutamos primero las pruebas relacionadas con clientes.
        cliente_principal = PruebasClientes.prueba_cliente_valido(self._gestor_clientes)
        PruebasClientes.prueba_email_invalido(self._gestor_clientes)
        PruebasClientes.prueba_nombre_invalido(self._gestor_clientes)
        PruebasClientes.prueba_cliente_duplicado(self._gestor_clientes)

        # Ejecutamos luego las pruebas relacionadas con servicios.
        sala, equipo, asesoria = PruebasServicios.prueba_servicios_validos(
            self._gestor_servicios
        )
        PruebasServicios.prueba_precio_invalido()

        # Ejecutamos las pruebas de reservas solo si existen sus dependencias.
        if cliente_principal and sala:
            PruebasReservas.prueba_reserva_exitosa(
                self._gestor_reservas,
                cliente_principal,
                sala,
            )

        # Ejecutamos validaciones de reserva sobre el servicio de equipos.
        if cliente_principal and equipo:
            PruebasReservas.prueba_duracion_invalida(
                self._gestor_reservas,
                cliente_principal,
                equipo,
            )
            PruebasReservas.prueba_confirmar_dos_veces(
                self._gestor_reservas,
                cliente_principal,
                equipo,
            )

        # Ejecutamos la prueba de indisponibilidad sobre asesorías.
        if cliente_principal and asesoria:
            PruebasReservas.prueba_servicio_no_disponible(
                self._gestor_reservas,
                cliente_principal,
                asesoria,
            )

        # Ejecutamos la prueba de descuento si el servicio de equipos existe.
        if equipo:
            PruebasReservas.prueba_descuento_por_volumen(
                self._gestor_clientes,
                self._gestor_reservas,
                equipo,
            )

        # Mostramos un cierre con estadísticas globales de la simulación.
        UtilidadesPruebas.resumen_final(
            self._gestor_clientes,
            self._gestor_servicios,
            self._gestor_reservas,
        )
        # Dejamos constancia de que la simulación completa terminó.
        logger.info("Simulacion completa. Todos los errores fueron manejados.")
        # Recordamos al usuario dónde puede revisar el historial completo.
        print("  Revisa 'sistema.log' para ver el registro completo.")

    def ejecutar_con_gestores(
        self,
        gestor_clientes: GestorClientes,
        gestor_servicios: GestorServicios,
        gestor_reservas: GestorReservas,
    ) -> None:
        # Reutilizamos gestores externos cuando la simulación se llama desde main.
        self._gestor_clientes = gestor_clientes
        # Reutilizamos el catálogo de servicios ya cargado por la sesión activa.
        self._gestor_servicios = gestor_servicios
        # Reutilizamos el gestor de reservas ya existente.
        self._gestor_reservas = gestor_reservas
        # Ejecutamos la simulación con ese contexto compartido.
        self.ejecutar()


# Esta función conserva la interfaz simple del código original.
def ejecutar_simulacion() -> None:
    # Creamos un simulador nuevo para una ejecución autónoma.
    simulador = Simulador()
    # Disparamos la simulación completa.
    simulador.ejecutar()


# Esta función conserva la interfaz usada por el menú principal.
def ejecutar_simulacion_con_gestores(
    gestor_clientes: GestorClientes,
    gestor_servicios: GestorServicios,
    gestor_reservas: GestorReservas,
) -> None:
    # Creamos un simulador nuevo que usará gestores externos.
    simulador = Simulador()
    # Ejecutamos la simulación con el contexto compartido recibido.
    simulador.ejecutar_con_gestores(
        gestor_clientes,
        gestor_servicios,
        gestor_reservas,
    )


# Este bloque permite correr la simulación directamente desde consola.
if __name__ == "__main__":
    # Ejecutamos la simulación completa con gestores nuevos.
    ejecutar_simulacion()
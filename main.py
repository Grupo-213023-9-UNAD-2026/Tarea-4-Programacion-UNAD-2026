"""
main.py
Autor: Ezequiel Olmos Luque(Líder)
Curso: Programación 213023 - UNAD
=======
Punto de entrada principal del sistema Software FJ.
Contiene el menú interactivo para clientes, servicios, reservas y reportes.
"""

# Importamos re para validar ciertos campos desde la interfaz.
import re

# Importamos el gestor de clientes para administrar el módulo correspondiente.
from cliente import GestorClientes
# Importamos los tipos concretos de servicio y su gestor.
from servicio import AlquilerEquipo, AsesoriaTecnica, GestorServicios, SalaReuniones
# Importamos el gestor de reservas y estados usados por el menú.
from reserva import ESTADO_CONFIRMADA, ESTADO_PENDIENTE, GestorReservas
# Importamos la excepción base del sistema para manejar errores de negocio.
from excepciones import ErrorSistema
# Importamos el logger para registrar sesiones y mostrar el log.
import logger
# Importamos la simulación automática para ejecutarla desde el menú.
import pruebas


# Definimos un patrón de nombre reutilizable para la captura de clientes.
PATRON_NOMBRE = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$")
# Definimos un patrón básico de correo reutilizable desde la interfaz.
PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")


# Esta clase agrupa utilidades simples de interacción por consola.
class Consola:
    """Funciones estáticas para pedir datos y mostrar secciones."""

    @staticmethod
    def titulo(texto: str) -> None:
        # Construimos un borde ancho para destacar títulos principales.
        borde = "=" * 60
        # Imprimimos una separación visual antes del título.
        print(f"\n{borde}")
        # Imprimimos el contenido del título centrado visualmente a la izquierda.
        print(f"  {texto}")
        # Cerramos el bloque con el mismo borde.
        print(borde)

    @staticmethod
    def subtitulo(texto: str) -> None:
        # Construimos un encabezado más corto para subsecciones del menú.
        print(f"\n-- {texto} --")

    @staticmethod
    def pausar() -> None:
        # Detenemos la ejecución hasta que el usuario presione ENTER.
        input("\nPresiona ENTER para continuar...")

    @staticmethod
    def pedir_texto(pregunta: str, obligatorio: bool = True) -> str:
        # Repetimos la captura hasta recibir un valor aceptable.
        while True:
            # Pedimos el dato y limpiamos espacios sobrantes.
            valor = input(f"{pregunta}: ").strip()
            # Si el dato es obligatorio y viene vacío, avisamos y repetimos.
            if obligatorio and not valor:
                print("[ATENCIÓN] Este campo no puede estar vacio.")
                continue
            # Devolvemos el valor cuando pasa la validación básica.
            return valor

    @staticmethod
    def pedir_numero(pregunta: str, tipo=float, minimo=None):
        # Repetimos la captura hasta convertir el valor correctamente.
        while True:
            try:
                # Leemos el texto, lo limpiamos y lo convertimos al tipo deseado.
                valor = tipo(input(f"{pregunta}: ").strip())
                # Si existe un mínimo y el valor no lo cumple, avisamos y repetimos.
                if minimo is not None and valor < minimo:
                    print(f"[ERROR] El valor debe ser mayor o igual a {minimo}.")
                    continue
                # Devolvemos el valor numérico ya validado.
                return valor
            except ValueError:
                # Informamos que el contenido ingresado no era numérico.
                print("[ERROR] Ingresa un numero valido.")

    @staticmethod
    def pedir_opcion(pregunta: str, opciones_validas: list[str]) -> str:
        # Repetimos la lectura hasta obtener una opción permitida.
        while True:
            # Capturamos la opción y la normalizamos a minúsculas.
            valor = input(f"{pregunta}: ").strip().lower()
            # Si la opción está permitida, la devolvemos.
            if valor in opciones_validas:
                return valor
            # Si no es válida, mostramos las alternativas posibles.
            print(f"[ERROR] Opcion invalida. Usa una de estas: {', '.join(opciones_validas)}")

    @staticmethod
    def confirmar(pregunta: str) -> bool:
        # Reutilizamos pedir_opcion para respuestas binarias del tipo s/n.
        return Consola.pedir_opcion(f"{pregunta} (s/n)", ["s", "n"]) == "s"

    @staticmethod
    def mostrar_lista(items, formateador=str, vacia: str = "No hay registros.") -> None:
        # Si la lista está vacía, mostramos el mensaje alternativo y salimos.
        if not items:
            print(vacia)
            return
        # Recorremos cada elemento con índice desde 1 para presentarlo al usuario.
        for indice, item in enumerate(items, start=1):
            # Aplicamos el formateador recibido para construir la línea visible.
            print(f"[{indice}] {formateador(item)}")

    @staticmethod
    def seleccionar_de_lista(items, nombre_item: str, formateador=str):
        # Si no hay elementos, no tiene sentido pedir selección.
        if not items:
            print(f"No hay {nombre_item}s disponibles.")
            return None
        # Mostramos la lista usando el formateador especificado.
        Consola.mostrar_lista(items, formateador=formateador)
        # Repetimos la lectura hasta obtener un índice válido.
        while True:
            try:
                # Permitimos cancelar con cero.
                opcion = int(input(f"Numero del {nombre_item} (0 para cancelar): ").strip())
                # Si el usuario digitó cero, devolvemos None para cancelar.
                if opcion == 0:
                    return None
                # Si el número está dentro del rango, devolvemos el objeto elegido.
                if 1 <= opcion <= len(items):
                    return items[opcion - 1]
                # Si salió del rango, mostramos una advertencia.
                print(f"[ATENCIÓN] Elige un numero entre 1 y {len(items)}.")
            except ValueError:
                # Si el dato no era entero, informamos y repetimos.
                print("[ERROR] Ingresa un numero entero valido.")

    @staticmethod
    def mostrar_error(error: Exception) -> None:
        # Normalizamos la forma de mostrar errores al usuario.
        print(f"[ERROR] {error}")

    @staticmethod
    def mostrar_ok(mensaje: str) -> None:
        # Normalizamos la forma de mostrar mensajes de éxito.
        print(f"[OK] {mensaje}")


# Esta clase maneja la interfaz del módulo de clientes.
class VistaClientes:
    """Interfaz de consola para registrar y consultar clientes."""

    def __init__(self, gestor_clientes: GestorClientes):
        # Guardamos el gestor recibido para delegar la lógica de negocio.
        self._gestor = gestor_clientes

    def menu(self) -> None:
        # Mantenemos activo el submenú hasta que el usuario decida salir.
        while True:
            # Mostramos el encabezado del módulo actual.
            Consola.titulo("GESTION DE CLIENTES")
            # Mostramos las opciones disponibles del submenú.
            print("[1] Registrar nuevo cliente")
            print("[2] Buscar cliente por documento")
            print("[3] Ver todos los clientes")
            print("[4] Activar o desactivar cliente")
            print("[0] Volver al menu principal")
            # Pedimos la opción y la validamos.
            opcion = Consola.pedir_opcion("Elige una opcion", ["0", "1", "2", "3", "4"])
            # Ejecutamos la acción correspondiente.
            if opcion == "1":
                self._registrar()
            elif opcion == "2":
                self._buscar()
            elif opcion == "3":
                self._listar()
            elif opcion == "4":
                self._cambiar_estado()
            elif opcion == "0":
                break

    def _pedir_identificacion(self) -> str | None:
        # Repetimos la captura hasta obtener una identificación válida o cancelar.
        while True:
            # Pedimos la identificación y permitimos cancelar.
            valor = Consola.pedir_texto("Numero de identificacion (o 'cancelar')")
            # Si el usuario quiere cancelar, devolvemos None.
            if valor.lower() == "cancelar":
                return None
            # Rechazamos identificaciones con caracteres no numéricos.
            if not valor.isdigit():
                print("[ERROR] Solo se permiten digitos.")
                continue
            # Rechazamos longitudes fuera del rango deseado.
            if not 5 <= len(valor) <= 15:
                print("[ERROR] La identificacion debe tener entre 5 y 15 digitos.")
                continue
            # Verificamos si la identificación ya existe dentro del gestor.
            try:
                self._gestor.buscar_por_id(valor)
                print("[ERROR] Ya existe un cliente con esa identificacion.")
                continue
            except ErrorSistema:
                # Si no existe, devolvemos el dato porque ya está disponible.
                return valor

    def _pedir_nombre(self) -> str | None:
        # Repetimos la captura hasta obtener un nombre válido o cancelar.
        while True:
            # Pedimos el nombre completo y permitimos cancelar.
            valor = Consola.pedir_texto("Nombre completo (o 'cancelar')")
            # Si el usuario quiere cancelar, devolvemos None.
            if valor.lower() == "cancelar":
                return None
            # Rechazamos nombres que no cumplan el patrón esperado.
            if not PATRON_NOMBRE.match(valor):
                print("[ERROR] El nombre solo puede contener letras y espacios.")
                continue
            # Si pasó la validación, devolvemos el nombre.
            return valor

    def _pedir_email(self) -> str | None:
        # Repetimos la captura hasta obtener un email válido o cancelar.
        while True:
            # Pedimos el correo y lo normalizamos en minúsculas.
            valor = Consola.pedir_texto("Correo electronico (o 'cancelar')").lower()
            # Si el usuario quiere cancelar, devolvemos None.
            if valor == "cancelar":
                return None
            # Rechazamos correos que no cumplan el patrón esperado.
            if not PATRON_EMAIL.match(valor):
                print("[ERROR] El correo debe verse como usuario@correo.com.")
                continue
            # Verificamos si el correo ya existe.
            try:
                self._gestor.buscar_por_email(valor)
                print("[ERROR] Ya existe un cliente con ese correo.")
                continue
            except ErrorSistema:
                # Si no existe, devolvemos el valor capturado.
                return valor

    def _pedir_telefono(self) -> str | None:
        # Repetimos la captura hasta obtener un teléfono válido o cancelar.
        while True:
            # Permitimos omitir el teléfono dejando el campo en blanco.
            valor = Consola.pedir_texto("Telefono (ENTER para omitir, o 'cancelar')", obligatorio=False)
            # Si el usuario quiere cancelar, devolvemos None.
            if valor.lower() == "cancelar":
                return None
            # Si no ingresó nada, devolvemos una cadena vacía.
            if not valor:
                return ""
            # Rechazamos teléfonos con caracteres no numéricos.
            if not valor.isdigit():
                print("[ERROR] El telefono solo puede contener digitos.")
                continue
            # Rechazamos longitudes fuera del rango deseado.
            if not 7 <= len(valor) <= 15:
                print("[ERROR] El telefono debe tener entre 7 y 15 digitos.")
                continue
            # Si pasó la validación, devolvemos el teléfono.
            return valor

    def _registrar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("REGISTRAR CLIENTE")
        # Pedimos la identificación y salimos si el usuario cancela.
        numero_id = self._pedir_identificacion()
        if numero_id is None:
            return
        # Pedimos el nombre y salimos si el usuario cancela.
        nombre = self._pedir_nombre()
        if nombre is None:
            return
        # Pedimos el correo y salimos si el usuario cancela.
        email = self._pedir_email()
        if email is None:
            return
        # Pedimos el teléfono y salimos si el usuario cancela.
        telefono = self._pedir_telefono()
        if telefono is None:
            return
        try:
            # Registramos el cliente usando el gestor de negocio.
            cliente = self._gestor.registrar_cliente(numero_id, nombre, email, telefono)
            # Informamos que el registro fue exitoso.
            Consola.mostrar_ok("Cliente registrado correctamente.")
            # Mostramos el detalle del cliente creado.
            print(cliente.describir())
        except ErrorSistema as error:
            # Si ocurre un error de negocio, lo mostramos de forma uniforme.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario lea el resultado.
        Consola.pausar()

    def _buscar(self) -> None:
        # Mostramos el encabezado de búsqueda.
        Consola.subtitulo("BUSCAR CLIENTE")
        # Pedimos la identificación del cliente buscado.
        numero_id = Consola.pedir_texto("Numero de identificacion")
        try:
            # Buscamos el cliente usando el gestor.
            cliente = self._gestor.buscar_por_id(numero_id)
            # Mostramos el detalle completo del cliente encontrado.
            print(cliente.describir())
        except ErrorSistema as error:
            # Mostramos cualquier error de negocio producido por la búsqueda.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario lea el resultado.
        Consola.pausar()

    def _listar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("LISTA DE CLIENTES")
        # Recuperamos la lista actual de clientes.
        clientes = self._gestor.listar_clientes()
        # Si no hay clientes, lo informamos.
        if not clientes:
            print("No hay clientes registrados todavia.")
        else:
            # Si sí hay clientes, mostramos el total.
            print(f"Total de clientes: {len(clientes)}\n")
            # Recorremos y mostramos la descripción completa de cada uno.
            for cliente in clientes:
                print(cliente.describir())
                print()
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()

    def _cambiar_estado(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("ACTIVAR O DESACTIVAR CLIENTE")
        # Recuperamos los clientes registrados para permitir selección.
        clientes = self._gestor.listar_clientes()
        # Pedimos al usuario que elija un cliente.
        cliente = Consola.seleccionar_de_lista(
            clientes,
            "cliente",
            formateador=lambda item: f"{item.nombre} | ID: {item.obtener_id()} | Estado: {'Activo' if item.activo else 'Inactivo'}",
        )
        # Si la selección fue cancelada, salimos sin hacer cambios.
        if cliente is None:
            return
        # Si el cliente está activo, lo desactivamos.
        if cliente.activo:
            cliente.desactivar()
            Consola.mostrar_ok(f"Cliente '{cliente.nombre}' desactivado.")
        else:
            # Si está inactivo, lo reactivamos.
            cliente.activar()
            Consola.mostrar_ok(f"Cliente '{cliente.nombre}' reactivado.")
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()


# Esta clase maneja la interfaz del módulo de servicios.
class VistaServicios:
    """Interfaz de consola para administrar el catálogo de servicios."""

    def __init__(self, gestor_servicios: GestorServicios):
        # Guardamos el gestor recibido para delegar la lógica.
        self._gestor = gestor_servicios

    def menu(self) -> None:
        # Mantenemos activo el submenú hasta que el usuario salga.
        while True:
            # Mostramos el encabezado del módulo actual.
            Consola.titulo("GESTION DE SERVICIOS")
            # Mostramos las opciones disponibles del submenú.
            print("[1] Agregar sala de reuniones")
            print("[2] Agregar alquiler de equipo")
            print("[3] Agregar asesoria tecnica")
            print("[4] Ver catalogo de servicios")
            print("[5] Activar o desactivar un servicio")
            print("[0] Volver al menu principal")
            # Pedimos la opción elegida por el usuario.
            opcion = Consola.pedir_opcion("Elige una opcion", ["0", "1", "2", "3", "4", "5"])
            # Ejecutamos la acción correspondiente.
            if opcion == "1":
                self._agregar_sala()
            elif opcion == "2":
                self._agregar_equipo()
            elif opcion == "3":
                self._agregar_asesoria()
            elif opcion == "4":
                self._listar()
            elif opcion == "5":
                self._cambiar_estado()
            elif opcion == "0":
                break

    def _agregar_sala(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("NUEVA SALA DE REUNIONES")
        # Capturamos los datos necesarios del nuevo servicio.
        nombre = Consola.pedir_texto("Nombre de la sala")
        precio = Consola.pedir_numero("Precio por hora", tipo=float, minimo=1)
        capacidad = Consola.pedir_numero("Capacidad maxima", tipo=int, minimo=1)
        try:
            # Creamos el objeto de dominio con los datos capturados.
            sala = SalaReuniones(nombre, precio, capacidad)
            # Agregamos el servicio al catálogo.
            self._gestor.agregar_servicio(sala)
            # Informamos que el registro fue exitoso.
            Consola.mostrar_ok("Sala registrada correctamente.")
            # Mostramos el detalle del servicio creado.
            print(sala.describir())
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()

    def _agregar_equipo(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("NUEVO ALQUILER DE EQUIPO")
        # Capturamos los datos necesarios del nuevo servicio.
        nombre = Consola.pedir_texto("Nombre del servicio")
        precio = Consola.pedir_numero("Precio por hora", tipo=float, minimo=1)
        tipo_equipo = Consola.pedir_texto("Tipo de equipo")
        try:
            # Creamos el objeto de dominio con los datos capturados.
            equipo = AlquilerEquipo(nombre, precio, tipo_equipo)
            # Agregamos el servicio al catálogo.
            self._gestor.agregar_servicio(equipo)
            # Informamos que el registro fue exitoso.
            Consola.mostrar_ok("Servicio de equipo registrado correctamente.")
            # Mostramos el detalle del servicio creado.
            print(equipo.describir())
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()

    def _agregar_asesoria(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("NUEVA ASESORIA TECNICA")
        # Capturamos los datos necesarios del nuevo servicio.
        nombre = Consola.pedir_texto("Nombre de la asesoria")
        precio = Consola.pedir_numero("Precio por hora", tipo=float, minimo=1)
        especialidad = Consola.pedir_texto("Especialidad")
        nivel = Consola.pedir_opcion("Nivel del asesor", ["junior", "senior", "experto"])
        try:
            # Creamos el objeto de dominio con los datos capturados.
            asesoria = AsesoriaTecnica(nombre, precio, especialidad, nivel)
            # Agregamos el servicio al catálogo.
            self._gestor.agregar_servicio(asesoria)
            # Informamos que el registro fue exitoso.
            Consola.mostrar_ok("Asesoria registrada correctamente.")
            # Mostramos el detalle del servicio creado.
            print(asesoria.describir())
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()

    def _listar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("CATALOGO DE SERVICIOS")
        # Recuperamos la lista actual del catálogo.
        servicios = self._gestor.listar_servicios()
        # Si no hay servicios, lo informamos.
        if not servicios:
            print("No hay servicios registrados todavia.")
        else:
            # Si sí hay servicios, mostramos el total.
            print(f"Total de servicios: {len(servicios)}\n")
            # Recorremos y mostramos la descripción completa de cada servicio.
            for servicio in servicios:
                print(servicio.describir())
                print()
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()

    def _cambiar_estado(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("ACTIVAR O DESACTIVAR SERVICIO")
        # Recuperamos los servicios disponibles en el catálogo.
        servicios = self._gestor.listar_servicios()
        # Pedimos al usuario que seleccione uno.
        servicio = Consola.seleccionar_de_lista(
            servicios,
            "servicio",
            formateador=lambda item: f"{item.nombre} | ID: {item.obtener_id()} | Estado: {'Disponible' if item.esta_disponible() else 'Inactivo'}",
        )
        # Si la selección fue cancelada, salimos sin hacer cambios.
        if servicio is None:
            return
        # Si el servicio está disponible, lo desactivamos.
        if servicio.esta_disponible():
            servicio.desactivar()
            Consola.mostrar_ok(f"Servicio '{servicio.nombre}' desactivado.")
        else:
            # Si estaba desactivado, lo reactivamos.
            servicio.activar()
            Consola.mostrar_ok(f"Servicio '{servicio.nombre}' reactivado.")
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()


# Esta clase maneja la interfaz del módulo de reservas.
class VistaReservas:
    """Interfaz de consola para crear, confirmar y procesar reservas."""

    def __init__(
        self,
        gestor_reservas: GestorReservas,
        gestor_clientes: GestorClientes,
        gestor_servicios: GestorServicios,
    ):
        # Guardamos el gestor de reservas para delegar su lógica.
        self._gestor = gestor_reservas
        # Guardamos el gestor de clientes para elegir quién reserva.
        self._gestor_clientes = gestor_clientes
        # Guardamos el gestor de servicios para elegir qué se reserva.
        self._gestor_servicios = gestor_servicios

    def menu(self) -> None:
        # Mantenemos activo el submenú hasta que el usuario lo cierre.
        while True:
            # Mostramos el encabezado del módulo actual.
            Consola.titulo("GESTION DE RESERVAS")
            # Mostramos las opciones disponibles del submenú.
            print("[1] Crear nueva reserva")
            print("[2] Confirmar una reserva")
            print("[3] Cancelar una reserva")
            print("[4] Procesar una reserva")
            print("[5] Ver todas las reservas")
            print("[6] Ver reservas por estado")
            print("[0] Volver al menu principal")
            # Pedimos la opción y la validamos.
            opcion = Consola.pedir_opcion("Elige una opcion", ["0", "1", "2", "3", "4", "5", "6"])
            # Ejecutamos la acción correspondiente.
            if opcion == "1":
                self._crear()
            elif opcion == "2":
                self._confirmar()
            elif opcion == "3":
                self._cancelar()
            elif opcion == "4":
                self._procesar()
            elif opcion == "5":
                self._listar_todas()
            elif opcion == "6":
                self._listar_por_estado()
            elif opcion == "0":
                break

    def _seleccionar_cliente(self):
        # Recuperamos todos los clientes registrados.
        clientes = self._gestor_clientes.listar_clientes()
        # Si no hay clientes, informamos y detenemos la operación.
        if not clientes:
            print("No hay clientes registrados. Debes crear uno antes de reservar.")
            return None
        # Pedimos al usuario que seleccione un cliente de la lista.
        cliente = Consola.seleccionar_de_lista(
            clientes,
            "cliente",
            formateador=lambda item: f"{item.nombre} | ID: {item.obtener_id()} | Estado: {'Activo' if item.activo else 'Inactivo'}",
        )
        # Si no eligió nada, devolvemos None.
        if cliente is None:
            return None
        # Si el cliente está inactivo, informamos y bloqueamos la reserva.
        if not cliente.activo:
            print(f"[WARN] El cliente '{cliente.nombre}' esta inactivo.")
            return None
        # Si todo está bien, devolvemos el cliente elegido.
        return cliente

    def _seleccionar_servicio(self):
        # Recuperamos solo los servicios disponibles para nuevas reservas.
        servicios = self._gestor_servicios.listar_servicios(solo_disponibles=True)
        # Si no hay servicios activos, lo informamos y detenemos la operación.
        if not servicios:
            print("No hay servicios disponibles en este momento.")
            return None
        # Pedimos al usuario que seleccione un servicio activo.
        return Consola.seleccionar_de_lista(
            servicios,
            "servicio",
            formateador=lambda item: f"{item.nombre} | ${item.precio_hora:,.0f}/hora | {type(item).__name__}",
        )

    def _crear(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("NUEVA RESERVA")
        # Solicitamos primero el cliente que hará la reserva.
        cliente = self._seleccionar_cliente()
        if cliente is None:
            Consola.pausar()
            return
        # Solicitamos luego el servicio a reservar.
        servicio = self._seleccionar_servicio()
        if servicio is None:
            Consola.pausar()
            return
        # Calculamos el mínimo sugerido según el tipo concreto de servicio.
        minimo_horas = getattr(servicio, "HORAS_MINIMAS", 0.1)
        # Pedimos la duración usando ese mínimo como validación previa.
        horas = Consola.pedir_numero(
            f"Duracion en horas (minimo {minimo_horas})",
            tipo=float,
            minimo=minimo_horas,
        )
        try:
            # Creamos la reserva con los datos capturados.
            reserva = self._gestor.crear_reserva(cliente, servicio, horas)
            # Informamos el éxito y mostramos el identificador generado.
            Consola.mostrar_ok("Reserva creada correctamente.")
            print(f"ID de la reserva: {reserva.id_reserva}")
            print(f"Estado inicial  : {reserva.estado}")
        except ErrorSistema as error:
            # Mostramos cualquier error de negocio ocurrido en la creación.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario vea el resultado.
        Consola.pausar()

    def _confirmar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("CONFIRMAR RESERVA")
        # Recuperamos solo las reservas pendientes de confirmación.
        pendientes = self._gestor.listar_por_estado(ESTADO_PENDIENTE)
        # Si no hay pendientes, lo informamos y terminamos.
        if not pendientes:
            print("No hay reservas pendientes de confirmacion.")
            Consola.pausar()
            return
        # Pedimos al usuario que elija una reserva pendiente.
        reserva = Consola.seleccionar_de_lista(
            pendientes,
            "reserva",
            formateador=lambda item: f"{item.id_reserva} | Cliente: {item.cliente.nombre} | Servicio: {item.servicio.nombre}",
        )
        # Si la selección fue cancelada, salimos.
        if reserva is None:
            return
        # Preparamos el diccionario de opciones específicas para el cálculo.
        kwargs = {}
        # Inspeccionamos el tipo concreto del servicio reservado.
        tipo_servicio = type(reserva.servicio).__name__
        # Si es una sala, preguntamos si el cálculo incluirá IVA.
        if tipo_servicio == "SalaReuniones":
            kwargs["aplicar_iva"] = Consola.confirmar("Aplicar IVA del 19%")
        # Si es alquiler de equipo, preguntamos cantidad y descuento.
        elif tipo_servicio == "AlquilerEquipo":
            cantidad = Consola.pedir_numero("Cantidad de equipos", tipo=int, minimo=1)
            kwargs["cantidad"] = cantidad
            kwargs["con_descuento"] = cantidad >= 3 and Consola.confirmar(
                "Aplicar descuento por volumen del 10%"
            )
        # Si es una asesoría, preguntamos por el informe escrito.
        elif tipo_servicio == "AsesoriaTecnica":
            kwargs["incluir_informe"] = Consola.confirmar("Incluir informe escrito (+15%)")
        try:
            # Confirmamos la reserva pasando los parámetros correspondientes.
            costo = reserva.confirmar(**kwargs)
            # Informamos el éxito y mostramos el costo final.
            Consola.mostrar_ok("Reserva confirmada correctamente.")
            print(f"Costo total: ${costo:,.2f} COP")
            print(reserva.describir())
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()

    def _cancelar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("CANCELAR RESERVA")
        # Recuperamos las reservas que siguen activas dentro del flujo.
        activas = [
            reserva
            for reserva in self._gestor.listar_todas()
            if reserva.estado in (ESTADO_PENDIENTE, ESTADO_CONFIRMADA)
        ]
        # Si no hay reservas activas, lo informamos y terminamos.
        if not activas:
            print("No hay reservas activas para cancelar.")
            Consola.pausar()
            return
        # Pedimos al usuario que elija la reserva a cancelar.
        reserva = Consola.seleccionar_de_lista(
            activas,
            "reserva",
            formateador=lambda item: f"{item.id_reserva} | Estado: {item.estado} | Cliente: {item.cliente.nombre}",
        )
        # Si la selección fue cancelada, salimos.
        if reserva is None:
            return
        # Pedimos un motivo opcional para registrar la cancelación.
        motivo = Consola.pedir_texto("Motivo de cancelacion", obligatorio=False)
        try:
            # Cancelamos la reserva usando el motivo capturado.
            reserva.cancelar(motivo)
            # Informamos que la reserva quedó cancelada.
            Consola.mostrar_ok("Reserva cancelada correctamente.")
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario lea el resultado.
        Consola.pausar()

    def _procesar(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("PROCESAR RESERVA")
        # Recuperamos solo las reservas ya confirmadas.
        confirmadas = self._gestor.listar_por_estado(ESTADO_CONFIRMADA)
        # Si no hay confirmadas, lo informamos y terminamos.
        if not confirmadas:
            print("No hay reservas confirmadas para procesar.")
            Consola.pausar()
            return
        # Pedimos al usuario que elija la reserva a procesar.
        reserva = Consola.seleccionar_de_lista(
            confirmadas,
            "reserva",
            formateador=lambda item: f"{item.id_reserva} | Cliente: {item.cliente.nombre} | Servicio: {item.servicio.nombre}",
        )
        # Si la selección fue cancelada, salimos.
        if reserva is None:
            return
        try:
            # Procesamos la reserva y recibimos el resumen final.
            resumen = reserva.procesar()
            # Informamos que el cierre fue exitoso.
            Consola.mostrar_ok("Reserva procesada correctamente.")
            # Mostramos el resumen generado por el modelo de reserva.
            print(resumen)
        except ErrorSistema as error:
            # Mostramos cualquier error controlado del dominio.
            Consola.mostrar_error(error)
        # Pausamos al final para que el usuario lea el resultado.
        Consola.pausar()

    def _listar_todas(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("TODAS LAS RESERVAS")
        # Recuperamos la lista completa de reservas.
        reservas = self._gestor.listar_todas()
        # Si no hay reservas, lo informamos.
        if not reservas:
            print("No hay reservas registradas todavia.")
        else:
            # Si sí hay reservas, mostramos el total.
            print(f"Total de reservas: {len(reservas)}\n")
            # Recorremos y mostramos la descripción completa de cada reserva.
            for reserva in reservas:
                print(reserva.describir())
                print()
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()

    def _listar_por_estado(self) -> None:
        # Mostramos el encabezado de la operación actual.
        Consola.subtitulo("RESERVAS POR ESTADO")
        # Pedimos el estado a filtrar usando las opciones válidas.
        estado = Consola.pedir_opcion(
            "Estado a filtrar",
            ["pendiente", "confirmada", "cancelada", "procesada"],
        )
        # Consultamos las reservas que coinciden con el estado elegido.
        reservas = self._gestor.listar_por_estado(estado)
        # Si no hay coincidencias, lo informamos.
        if not reservas:
            print(f"No hay reservas en estado {estado.upper()}.")
        else:
            # Si sí hay coincidencias, mostramos cuántas fueron halladas.
            print(f"Reservas encontradas en estado {estado.upper()}: {len(reservas)}\n")
            # Recorremos y mostramos la descripción de cada una.
            for reserva in reservas:
                print(reserva.describir())
                print()
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()


# Esta clase maneja la visualización de estadísticas simples del sistema.
class VistaReportes:
    """Interfaz de consola para mostrar totales e ingresos."""

    def __init__(
        self,
        gestor_clientes: GestorClientes,
        gestor_servicios: GestorServicios,
        gestor_reservas: GestorReservas,
    ):
        # Guardamos el gestor de clientes para consultar su total.
        self._gestor_clientes = gestor_clientes
        # Guardamos el gestor de servicios para consultar su total.
        self._gestor_servicios = gestor_servicios
        # Guardamos el gestor de reservas para consultar totales e ingresos.
        self._gestor_reservas = gestor_reservas

    def mostrar(self) -> None:
        # Mostramos el encabezado del módulo de reportes.
        Consola.titulo("REPORTES DEL SISTEMA")
        # Calculamos los conteos y el valor de ingresos procesados.
        total_clientes = self._gestor_clientes.total_clientes()
        total_servicios = self._gestor_servicios.total_servicios()
        total_reservas = self._gestor_reservas.total_reservas()
        ingresos = self._gestor_reservas.ingresos_totales()
        # Mostramos el resumen de las métricas principales.
        print(f"Clientes registrados  : {total_clientes}")
        print(f"Servicios en catalogo : {total_servicios}")
        print(f"Reservas totales      : {total_reservas}")
        print(f"Ingresos procesados   : ${ingresos:,.2f} COP")
        # Ofrecemos la visualización rápida del log reciente.
        if Consola.confirmar("Deseas ver las ultimas lineas del log"):
            logger.mostrar_log(30)
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()


# Esta clase orquesta todo el sistema y enlaza gestores con vistas.
class SistemaSoftwareFJ:
    """Clase principal del programa interactivo."""

    def __init__(self):
        # Creamos el gestor principal de clientes.
        self._gestor_clientes = GestorClientes()
        # Creamos el gestor principal del catálogo de servicios.
        self._gestor_servicios = GestorServicios()
        # Creamos el gestor principal de reservas.
        self._gestor_reservas = GestorReservas()
        # Creamos la vista de clientes enlazada con su gestor.
        self._vista_clientes = VistaClientes(self._gestor_clientes)
        # Creamos la vista de servicios enlazada con su gestor.
        self._vista_servicios = VistaServicios(self._gestor_servicios)
        # Creamos la vista de reservas enlazada con los tres gestores necesarios.
        self._vista_reservas = VistaReservas(
            self._gestor_reservas,
            self._gestor_clientes,
            self._gestor_servicios,
        )
        # Creamos la vista de reportes enlazada con los tres gestores.
        self._vista_reportes = VistaReportes(
            self._gestor_clientes,
            self._gestor_servicios,
            self._gestor_reservas,
        )

    def _ejecutar_simulacion(self) -> None:
        # Mostramos un título claro para la simulación automática.
        Consola.titulo("SIMULACION AUTOMATICA")
        # Recordamos al usuario qué hará esta opción.
        print("Se ejecutaran 11 operaciones de prueba sobre la sesion actual.")
        # Solo ejecutamos la simulación si el usuario confirma.
        if Consola.confirmar("Deseas continuar"):
            pruebas.ejecutar_simulacion_con_gestores(
                self._gestor_clientes,
                self._gestor_servicios,
                self._gestor_reservas,
            )
        # Pausamos al final para conservar la salida visible.
        Consola.pausar()

    def _menu_principal(self) -> None:
        # Registramos el inicio de la sesión actual en el log.
        logger.iniciar_sesion()
        # Mantenemos activo el menú principal hasta que el usuario salga.
        while True:
            # Mostramos el encabezado principal del programa.
            Consola.titulo("SISTEMA SOFTWARE FJ")
            # Mostramos una breve descripción del sistema.
            print("Gestion de Clientes, Servicios y Reservas")
            print()
            # Mostramos las opciones principales.
            print("[1] Gestion de Clientes")
            print("[2] Gestion de Servicios")
            print("[3] Gestion de Reservas")
            print("[4] Reportes y estadisticas")
            print("[5] Ejecutar simulacion automatica")
            print("[0] Salir")
            # Pedimos la opción elegida por el usuario.
            opcion = Consola.pedir_opcion("Elige una opcion", ["0", "1", "2", "3", "4", "5"])
            # Despachamos la opción correspondiente.
            if opcion == "1":
                self._vista_clientes.menu()
            elif opcion == "2":
                self._vista_servicios.menu()
            elif opcion == "3":
                self._vista_reservas.menu()
            elif opcion == "4":
                self._vista_reportes.mostrar()
            elif opcion == "5":
                self._ejecutar_simulacion()
            elif opcion == "0":
                print("\nSistema cerrado. Hasta pronto.")
                print("El historial quedo guardado en sistema.log.\n")
                break

    def iniciar(self) -> None:
        # Lanzamos el menú principal del sistema.
        self._menu_principal()


# Este bloque convierte el archivo en el punto de entrada del programa.
if __name__ == "__main__":
    # Creamos la instancia principal del sistema interactivo.
    sistema = SistemaSoftwareFJ()
    # Arrancamos la ejecución del menú principal.
    sistema.iniciar()

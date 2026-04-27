"""
main.py
=======
Punto de entrada del sistema Software FJ.
VERSIÓN REFACTORIZADA CON CLASES (POO)

Incluye un menú interactivo para hacer pruebas reales desde la consola.
Organizado en clases siguiendo los principios de Programación Orientada a Objetos.

Ejecución:  python main.py
Requisitos: Python 3.10 o superior. Sin librerías externas.

Autor: Ezequiel Olmos Luque(Líder)
Curso: Programación 213023 - UNAD
"""

# Importamos las clases necesarias de otros archivos del proyecto
from cliente import GestorClientes  # Para manejar clientes
from servicio import SalaReuniones, AlquilerEquipo, AsesoriaTecnica, GestorServicios  # Para manejar servicios
from reserva import GestorReservas, ESTADO_PENDIENTE, ESTADO_CONFIRMADA  # Para manejar reservas y sus estados
from excepciones import ErrorSistema  # Para capturar errores personalizados
import logger  # Para registrar eventos en el archivo sistema.log
import pruebas  # Para ejecutar la simulación automática de 11 pruebas


# ─────────────────────────────────────────────
# CLASE PARA UTILIDADES DE CONSOLA
# ─────────────────────────────────────────────

class Consola:
    """
    Clase que agrupa todas las utilidades de interacción con la consola.
    Principio OOP: ENCAPSULACIÓN de funciones de entrada/salida.
    
    Esta clase contiene métodos estáticos (no necesita crear un objeto)
    para mostrar títulos, pedir datos, mostrar listas, etc.
    """

    @staticmethod
    def limpiar():
        """Imprime líneas en blanco para simular limpieza de pantalla."""
        print("\n" * 2)  # Salta dos líneas para "limpiar" visualmente

    @staticmethod
    def titulo(texto):
        """Imprime un título destacado con borde de doble línea."""
        borde = "═" * 55  # Crea una línea de 55 caracteres "═"
        print(f"\n{borde}")  # Imprime el borde superior
        print(f"  {texto}")  # Imprime el texto centrado
        print(f"{borde}")   # Imprime el borde inferior

    @staticmethod
    def subtitulo(texto):
        """Imprime un subtítulo con borde de línea simple."""
        print(f"\n  ── {texto} ──")  # Línea simple antes y después del texto

    @staticmethod
    def pausar():
        """Pausa la ejecución hasta que el usuario presione ENTER."""
        input("\n  Presiona ENTER para continuar...")  # Espera que el usuario presione ENTER

    @staticmethod
    def pedir(pregunta, obligatorio=True):
        """
        Pide un dato al usuario.
        Si es obligatorio (True) no permite entrada vacía.
        Retorna el valor ingresado como string.
        """
        while True:  # Bucle infinito hasta que el usuario ingrese algo válido
            valor = input(f"  {pregunta}: ").strip()  # Muestra la pregunta y elimina espacios
            if valor or not obligatorio:  # Si hay texto o no es obligatorio
                return valor  # Devuelve el valor ingresado
            print("  ⚠ Este campo no puede estar vacío. Intenta de nuevo.")  # Mensaje de error

    @staticmethod
    def pedir_numero(pregunta, tipo=float, minimo=None):
        """
        Pide un número al usuario con validación de tipo y valor mínimo.
        tipo: float (decimal) o int (entero) - por defecto float
        minimo: valor mínimo permitido (opcional)
        """
        while True:  # Bucle hasta que ingrese un número válido
            try:
                valor = tipo(input(f"  {pregunta}: ").strip())  # Convierte a número
                if minimo is not None and valor < minimo:  # Si hay mínimo y no lo cumple
                    print(f"  ⚠ El valor debe ser mayor o igual a {minimo}.")
                    continue  # Vuelve a pedir
                return valor  # Devuelve el número válido
            except ValueError:  # Si no se puede convertir a número
                print(f"  ⚠ Ingresa un número válido.")

    @staticmethod
    def pedir_opcion(pregunta, opciones_validas):
        """
        Pide una opción al usuario y valida que esté dentro de las opciones permitidas.
        Retorna la opción seleccionada (en minúsculas).
        """
        while True:
            valor = input(f"  {pregunta}: ").strip().lower()  # Pide y convierte a minúsculas
            if valor in opciones_validas:  # Si está en la lista de opciones
                return valor
            print(f"  ⚠ Opción inválida. Opciones: {', '.join(opciones_validas)}")  # Muestra opciones válidas

    @staticmethod
    def mostrar_lista(items, vacia="No hay registros."):
        """
        Imprime una lista numerada de objetos.
        items: lista de objetos a mostrar
        vacia: mensaje a mostrar si la lista está vacía
        """
        if not items:  # Si la lista está vacía
            print(f"  {vacia}")  # Muestra mensaje personalizado
            return
        for i, item in enumerate(items, 1):  # Recorre la lista con índice desde 1
            print(f"  [{i}] {item}")  # Muestra cada elemento numerado

    @staticmethod
    def seleccionar_de_lista(items, nombre_item="elemento"):
        """
        Muestra una lista numerada y pide al usuario que seleccione un elemento.
        Retorna el elemento seleccionado o None si se cancela.
        """
        Consola.mostrar_lista(items)  # Primero muestra la lista
        if not items:  # Si no hay elementos
            return None
        
        while True:  # Bucle hasta que seleccione una opción válida
            try:
                idx = int(input(f"\n  Número del {nombre_item} (0 para cancelar): "))
                if idx == 0:  # 0 cancela la operación
                    return None
                if 1 <= idx <= len(items):  # Si el índice está en rango
                    return items[idx - 1]  # Devuelve el elemento (restamos 1 porque la lista empieza en 0)
                print(f"  ⚠ Número fuera de rango. Elige entre 1 y {len(items)}.")
            except ValueError:  # Si no ingresa un número
                print("  ⚠ Ingresa un número entero.")


# ─────────────────────────────────────────────
# CLASE PARA GESTIÓN DE CLIENTES (VISTA)
# ─────────────────────────────────────────────

class VistaClientes:
    """
    Clase que maneja la interfaz de usuario para la gestión de clientes.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES (Vista vs Gestor)
    
    Esta clase solo se encarga de mostrar menús y pedir datos al usuario.
    Los cálculos y validaciones los hace el GestorClientes.
    """

    def __init__(self, gestor_clientes: GestorClientes):
        """
        Constructor de la vista de clientes.
        Recibe el gestor de clientes como dependencia (inyección de dependencias).
        Esto permite que la vista use el gestor sin tener que crearlo ella misma.
        """
        self._gestor = gestor_clientes  # Guarda el gestor en un atributo privado

    def menu(self):
        """Submenú completo de gestión de clientes."""
        while True:  # Bucle infinito para el submenú
            Consola.titulo("GESTIÓN DE CLIENTES")  # Muestra título
            # Muestra las opciones disponibles
            print("  [1] Registrar nuevo cliente")
            print("  [2] Buscar cliente por Documento")
            print("  [3] Ver todos los clientes")
            print("  [4] Desactivar / reactivar cliente")
            print("  [0] Volver al menú principal")

            # Pide la opción y valida que sea una de las permitidas
            opcion = Consola.pedir_opcion("Elige una opción", ["0", "1", "2", "3", "4"])

            # Ejecuta la función correspondiente según la opción
            if opcion == "1":
                self._registrar()  # Registrar nuevo cliente
            elif opcion == "2":
                self._buscar()     # Buscar cliente por ID
            elif opcion == "3":
                self._listar()     # Mostrar todos los clientes
            elif opcion == "4":
                self._cambiar_estado()  # Activar o desactivar cliente
            elif opcion == "0":
                break  # Salir del submenú

    def _registrar(self):
        """Registra un nuevo cliente en el sistema."""
        Consola.subtitulo("REGISTRAR CLIENTE")
        print("  (Escribe 'cancelar' en cualquier campo para salir)\n")

        import re  # Importamos expresiones regulares para validar formatos

        # ── NÚMERO DE IDENTIFICACIÓN ──
        # Validación: solo dígitos, entre 5 y 15 caracteres, no duplicado
        numero_id = None
        while True:
            valor = input("  Número de identificación (cédula/NIT): ").strip()

            # Permite cancelar la operación
            if valor.lower() == "cancelar":
                print("\n  Registro cancelado.")
                Consola.pausar()
                return

            # Validación: campo vacío
            if not valor:
                print("  ✘ El número de identificación no puede estar vacío.\n")
                continue

            # Validación: solo dígitos
            if not valor.isdigit():
                print("  ✘ Solo se permiten dígitos.\n")
                continue

            # Validación: longitud entre 5 y 15
            if not (5 <= len(valor) <= 15):
                print(f"  ✘ Debe tener entre 5 y 15 dígitos (ingresaste {len(valor)}).\n")
                continue

            # Validación: que no exista ya un cliente con esa identificación
            try:
                self._gestor.buscar_por_id(valor)  # Si encuentra, lanza excepción
                print(f"  ✘ Ya existe un cliente con la identificación '{valor}'.\n")
                continue
            except ErrorSistema:
                pass  # No existe, está disponible

            numero_id = valor  # Guarda el valor válido
            print(f"  ✔ Identificación aceptada: {numero_id}\n")
            break

        # ── NOMBRE ──
        # Validación: solo letras, espacios, tildes y eñes
        nombre = None
        while True:
            valor = input("  Nombre completo: ").strip()

            if valor.lower() == "cancelar":
                print("\n  Registro cancelado.")
                Consola.pausar()
                return

            if not valor:
                print("  ✘ El nombre no puede estar vacío.\n")
                continue

            # Expresión regular: letras (incluyendo tildes), espacios y eñes
            if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$", valor):
                print("  ✘ El nombre solo puede contener letras y espacios.\n")
                continue

            nombre = valor
            print(f"  ✔ Nombre aceptado: {nombre}\n")
            break

        # ── EMAIL ──
        # Validación: formato usuario@dominio.extensión
        email = None
        while True:
            valor = input("  Correo electrónico: ").strip().lower()

            if valor == "cancelar":
                print("\n  Registro cancelado.")
                Consola.pausar()
                return

            if not valor:
                print("  ✘ El email no puede estar vacío.\n")
                continue

            # Expresión regular para validar email
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", valor):
                print("  ✘ Formato inválido. Debe ser como: usuario@correo.com\n")
                continue

            # Validación: email no duplicado
            try:
                self._gestor.buscar_por_email(valor)
                print(f"  ✘ El email '{valor}' ya está registrado.\n")
                continue
            except ErrorSistema:
                pass

            email = valor
            print(f"  ✔ Email aceptado: {email}\n")
            break

        # ── TELÉFONO (opcional) ──
        # Validación: solo dígitos, entre 7 y 15 caracteres
        telefono = ""
        while True:
            valor = input("  Teléfono (opcional, ENTER para omitir): ").strip()

            if valor.lower() == "cancelar":
                print("\n  Registro cancelado.")
                Consola.pausar()
                return

            if not valor:
                print("  ✔ Teléfono omitido.\n")
                break

            if not valor.isdigit():
                print("  ✘ El teléfono solo puede contener dígitos.\n")
                continue

            if not (7 <= len(valor) <= 15):
                print(f"  ✘ El teléfono debe tener entre 7 y 15 dígitos.\n")
                continue

            telefono = valor
            print(f"  ✔ Teléfono aceptado: {telefono}\n")
            break

        # ── REGISTRO FINAL ──
        # Crea el cliente usando el gestor
        try:
            cliente = self._gestor.registrar_cliente(numero_id, nombre, email, telefono)
            print("  " + "─" * 45)
            print("  ✔ ¡Cliente registrado exitosamente!")
            print("  " + "─" * 45)
            print(cliente.describir())  # Muestra los datos del cliente
        except ErrorSistema as e:
            print(f"\n  ✘ Error inesperado al guardar: {e}")
        Consola.pausar()

    def _buscar(self):
        """Busca un cliente por su número de identificación."""
        Consola.subtitulo("BUSCAR CLIENTE")
        numero_id = Consola.pedir("Número de identificación del cliente")
        try:
            cliente = self._gestor.buscar_por_id(numero_id)  # Busca en el gestor
            print(f"\n  Cliente encontrado:")
            print(cliente.describir())  # Muestra los datos
        except ErrorSistema as e:
            print(f"\n  ✘ {e}")  # Muestra el error si no existe
        Consola.pausar()

    def _listar(self):
        """Muestra la lista completa de todos los clientes."""
        Consola.subtitulo("LISTA DE CLIENTES")
        clientes = self._gestor.listar_clientes()  # Obtiene la lista
        if not clientes:
            print("  No hay clientes registrados todavía.")
        else:
            print(f"  Total: {len(clientes)} cliente(s)\n")
            for c in clientes:  # Recorre y muestra cada cliente
                print(c.describir())
                print()
        Consola.pausar()

    def _cambiar_estado(self):
        """Permite activar o desactivar un cliente (baja lógica)."""
        Consola.subtitulo("ACTIVAR / DESACTIVAR CLIENTE")
        clientes = self._gestor.listar_clientes()
        cliente = Consola.seleccionar_de_lista(clientes, "cliente")  # Selecciona uno
        if not cliente:
            return
        if cliente.activo:  # Si está activo, lo desactiva
            cliente.desactivar()
            print(f"\n  ⚠ Cliente '{cliente.nombre}' desactivado.")
        else:  # Si está inactivo, lo activa
            cliente.activar()
            print(f"\n  ✔ Cliente '{cliente.nombre}' reactivado.")
        Consola.pausar()


# ─────────────────────────────────────────────
# CLASE PARA GESTIÓN DE SERVICIOS (VISTA)
# ─────────────────────────────────────────────

class VistaServicios:
    """
    Clase que maneja la interfaz de usuario para la gestión de servicios.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES (Vista vs Gestor)
    
    Similar a VistaClientes, pero para servicios.
    """

    def __init__(self, gestor_servicios: GestorServicios):
        """Constructor: recibe el gestor de servicios como dependencia."""
        self._gestor = gestor_servicios

    def menu(self):
        """Submenú completo de gestión de servicios."""
        while True:
            Consola.titulo("GESTIÓN DE SERVICIOS")
            # Opciones del menú de servicios
            print("  [1] Agregar sala de reuniones")
            print("  [2] Agregar alquiler de equipo")
            print("  [3] Agregar asesoría técnica")
            print("  [4] Ver catálogo de servicios")
            print("  [5] Activar / desactivar un servicio")
            print("  [0] Volver al menú principal")

            opcion = Consola.pedir_opcion("Elige una opción", ["0", "1", "2", "3", "4", "5"])

            # Ejecuta la función según la opción
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

    def _agregar_sala(self):
        """Agrega una nueva sala de reuniones al catálogo."""
        Consola.subtitulo("NUEVA SALA DE REUNIONES")
        # Pide los datos necesarios
        nombre = Consola.pedir("Nombre de la sala")
        precio = Consola.pedir_numero("Precio por hora (pesos)", tipo=float, minimo=1)
        capacidad = Consola.pedir_numero("Capacidad máxima (personas)", tipo=int, minimo=1)
        try:
            # Crea la sala y la agrega al gestor
            sala = SalaReuniones(nombre, precio, capacidad)
            self._gestor.agregar_servicio(sala)
            print(f"\n  ✔ Sala registrada:")
            print(sala.describir())
        except ErrorSistema as e:
            print(f"\n  ✘ Error: {e}")
        Consola.pausar()

    def _agregar_equipo(self):
        """Agrega un nuevo servicio de alquiler de equipo al catálogo."""
        Consola.subtitulo("NUEVO ALQUILER DE EQUIPO")
        nombre = Consola.pedir("Nombre del servicio")
        precio = Consola.pedir_numero("Precio por hora (pesos)", tipo=float, minimo=1)
        tipo_equipo = Consola.pedir("Tipo de equipo (ej: Portátil, Proyector, Tablet)")
        try:
            equipo = AlquilerEquipo(nombre, precio, tipo_equipo)
            self._gestor.agregar_servicio(equipo)
            print(f"\n  ✔ Equipo registrado:")
            print(equipo.describir())
        except ErrorSistema as e:
            print(f"\n  ✘ Error: {e}")
        Consola.pausar()

    def _agregar_asesoria(self):
        """Agrega una nueva asesoría técnica al catálogo."""
        Consola.subtitulo("NUEVA ASESORÍA TÉCNICA")
        nombre = Consola.pedir("Nombre de la asesoría")
        precio = Consola.pedir_numero("Precio por hora (pesos)", tipo=float, minimo=1)
        especialidad = Consola.pedir("Especialidad (ej: Desarrollo Web, Seguridad)")
        print("  Niveles disponibles: junior | senior | experto")
        nivel = Consola.pedir_opcion("Nivel del asesor", ["junior", "senior", "experto"])
        try:
            asesoria = AsesoriaTecnica(nombre, precio, especialidad, nivel)
            self._gestor.agregar_servicio(asesoria)
            print(f"\n  ✔ Asesoría registrada:")
            print(asesoria.describir())
        except ErrorSistema as e:
            print(f"\n  ✘ Error: {e}")
        Consola.pausar()

    def _listar(self):
        """Muestra el catálogo completo de servicios disponibles."""
        Consola.subtitulo("CATÁLOGO DE SERVICIOS")
        servicios = self._gestor.listar_servicios()  # Obtiene todos los servicios
        if not servicios:
            print("  No hay servicios en el catálogo todavía.")
        else:
            print(f"  Total: {len(servicios)} servicio(s)\n")
            for s in servicios:  # Recorre y muestra cada servicio
                print(s.describir())
                print()
        Consola.pausar()

    def _cambiar_estado(self):
        """Permite activar o desactivar un servicio."""
        Consola.subtitulo("ACTIVAR / DESACTIVAR SERVICIO")
        servicios = self._gestor.listar_servicios()
        servicio = Consola.seleccionar_de_lista(servicios, "servicio")
        if not servicio:
            return
        if servicio.esta_disponible():  # Si está disponible, lo desactiva
            servicio.desactivar()
            print(f"\n  ⚠ Servicio '{servicio.nombre}' desactivado.")
        else:  # Si no está disponible, lo activa
            servicio.activar()
            print(f"\n  ✔ Servicio '{servicio.nombre}' reactivado.")
        Consola.pausar()


# ─────────────────────────────────────────────
# CLASE PARA GESTIÓN DE RESERVAS (VISTA)
# ─────────────────────────────────────────────

class VistaReservas:
    """
    Clase que maneja la interfaz de usuario para la gestión de reservas.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES (Vista vs Gestor)
    
    Esta clase necesita acceso a los tres gestores (clientes, servicios y reservas)
    porque para crear una reserva necesita saber qué clientes y servicios existen.
    """

    def __init__(self, gestor_reservas: GestorReservas, 
                 gestor_clientes: GestorClientes,
                 gestor_servicios: GestorServicios):
        """
        Constructor: recibe los tres gestores como dependencias.
        """
        self._gestor = gestor_reservas  # Gestor de reservas
        self._gestor_clientes = gestor_clientes  # Gestor de clientes
        self._gestor_servicios = gestor_servicios  # Gestor de servicios

    def menu(self):
        """Submenú completo de gestión de reservas."""
        while True:
            Consola.titulo("GESTIÓN DE RESERVAS")
            print("  [1] Crear nueva reserva")
            print("  [2] Confirmar una reserva (calcular costo)")
            print("  [3] Cancelar una reserva")
            print("  [4] Procesar una reserva (marcar como entregada)")
            print("  [5] Ver todas las reservas")
            print("  [6] Ver reservas por estado")
            print("  [0] Volver al menú principal")

            opcion = Consola.pedir_opcion("Elige una opción", ["0", "1", "2", "3", "4", "5", "6"])

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

    def _crear(self):
        """Crea una nueva reserva seleccionando cliente y servicio."""
        Consola.subtitulo("NUEVA RESERVA")

        # ── SELECCIONAR CLIENTE ──
        print("\n  Clientes disponibles:")
        clientes = self._gestor_clientes.listar_clientes()  # Obtiene todos los clientes

        # Si no hay clientes, no se puede crear reserva
        if not clientes:
            print("  ✘ No hay clientes registrados.")
            print("  Debes registrar al menos un cliente antes de crear una reserva.")
            Consola.pausar()
            return

        # Muestra lista de clientes numerada
        for i, c in enumerate(clientes, 1):
            estado = "✓" if c.activo else "✗"  # ✓ = activo, ✗ = inactivo
            print(f"  [{i}] {estado} {c.nombre} - ID: {c.obtener_id()}")

        # Pide al usuario que seleccione un cliente por número
        try:
            idx_cliente = int(input("\n  Número del cliente (0 para cancelar): ").strip())
            if idx_cliente == 0:
                return
            if 1 <= idx_cliente <= len(clientes):
                cliente = clientes[idx_cliente - 1]
            else:
                print("  ✘ Número inválido.")
                Consola.pausar()
                return
        except ValueError:
            print("  ✘ Debes ingresar un número válido.")
            Consola.pausar()
            return

        # Verifica que el cliente esté activo
        if not cliente.activo:
            print(f"  ✘ El cliente '{cliente.nombre}' está desactivado.")
            Consola.pausar()
            return

        print(f"\n  ✓ Cliente seleccionado: {cliente.nombre}")

        # ── SELECCIONAR SERVICIO ──
        print("\n  Servicios disponibles:")
        servicios = self._gestor_servicios.listar_servicios(solo_disponibles=True)  # Solo servicios activos

        if not servicios:
            print("  ✘ No hay servicios disponibles.")
            Consola.pausar()
            return

        # Muestra lista de servicios numerada
        for i, s in enumerate(servicios, 1):
            print(f"  [{i}] {s.nombre} - ${s.precio_hora:,.0f}/hora - {type(s).__name__}")

        try:
            idx_servicio = int(input("\n  Número del servicio (0 para cancelar): ").strip())
            if idx_servicio == 0:
                return
            if 1 <= idx_servicio <= len(servicios):
                servicio = servicios[idx_servicio - 1]
            else:
                print("  ✘ Número inválido.")
                Consola.pausar()
                return
        except ValueError:
            print("  ✘ Debes ingresar un número válido.")
            Consola.pausar()
            return

        print(f"\n  ✓ Servicio seleccionado: {servicio.nombre}")

        # ── DURACIÓN ──
        horas = Consola.pedir_numero("Duración en horas (mínimo 0.5)", tipo=float, minimo=0.1)

        # ── CREAR RESERVA ──
        try:
            reserva = self._gestor.crear_reserva(cliente, servicio, horas)
            print(f"\n  ✔ ¡RESERVA CREADA EXITOSAMENTE!")
            print(f"  ID de tu reserva: {reserva.id_reserva}")
            print(f"  Estado actual   : {reserva.estado}")
        except ErrorSistema as e:
            print(f"\n  ✘ Error al crear la reserva: {e}")

        Consola.pausar()

    def _confirmar(self):
        """Confirma una reserva pendiente y calcula su costo final."""
        Consola.subtitulo("CONFIRMAR RESERVA")

        # Obtiene solo las reservas pendientes
        pendientes = self._gestor.listar_por_estado(ESTADO_PENDIENTE)

        if not pendientes:
            print("  No hay reservas pendientes de confirmación.")
            Consola.pausar()
            return

        # Muestra las reservas pendientes
        print(f"\n  Reservas pendientes:")
        for i, r in enumerate(pendientes, 1):
            print(f"  [{i}] ID: {r.id_reserva} | Cliente: {r.cliente.nombre} | Servicio: {r.servicio.nombre}")

        # Selecciona una reserva
        try:
            idx = int(input("\n  Número de la reserva a confirmar (0 para cancelar): ").strip())
            if idx == 0:
                return
            if 1 <= idx <= len(pendientes):
                reserva = pendientes[idx - 1]
            else:
                print("  ✘ Número inválido.")
                Consola.pausar()
                return
        except ValueError:
            print("  ✘ Debes ingresar un número válido.")
            Consola.pausar()
            return

        # Parámetros según el tipo de servicio (cada servicio tiene opciones diferentes)
        kwargs = {}
        tipo = type(reserva.servicio).__name__

        if tipo == "SalaReuniones":
            # Para salas: pregunta si aplicar IVA del 19%
            resp = Consola.pedir_opcion("¿Aplicar IVA del 19%? (s/n)", ["s", "n"])
            kwargs["aplicar_iva"] = (resp == "s")

        elif tipo == "AlquilerEquipo":
            # Para equipos: pregunta cantidad y si aplicar descuento
            cantidad = Consola.pedir_numero("¿Cuántos equipos?", tipo=int, minimo=1)
            kwargs["cantidad"] = cantidad
            if cantidad >= 3:  # Descuento solo para 3 o más equipos
                resp = Consola.pedir_opcion("¿Aplicar descuento por volumen 10%? (s/n)", ["s", "n"])
                kwargs["con_descuento"] = (resp == "s")

        elif tipo == "AsesoriaTecnica":
            # Para asesorías: pregunta si incluir informe escrito
            resp = Consola.pedir_opcion("¿Incluir informe escrito (+15%)? (s/n)", ["s", "n"])
            kwargs["incluir_informe"] = (resp == "s")

        # Confirma la reserva y calcula el costo
        try:
            costo = reserva.confirmar(**kwargs)
            print(f"\n  ✔ ¡RESERVA CONFIRMADA!")
            print(f"  Costo total: ${costo:,.2f} COP")
            print(reserva.describir())
        except ErrorSistema as e:
            print(f"\n  ✘ Error al confirmar: {e}")

        Consola.pausar()

    def _cancelar(self):
        """Cancela una reserva (solo si está pendiente o confirmada)."""
        Consola.subtitulo("CANCELAR RESERVA")

        # Obtiene todas las reservas
        todas = self._gestor.listar_todas()
        # Filtra solo las activas (pendientes o confirmadas)
        activas = [r for r in todas if r.estado in (ESTADO_PENDIENTE, ESTADO_CONFIRMADA)]

        if not activas:
            print("  No hay reservas activas para cancelar.")
            Consola.pausar()
            return

        # Muestra las reservas activas
        for i, r in enumerate(activas, 1):
            print(f"  [{i}] ID: {r.id_reserva} | Estado: {r.estado} | Cliente: {r.cliente.nombre}")

        try:
            idx = int(input("\n  Número de la reserva a cancelar (0 para cancelar): ").strip())
            if idx == 0:
                return
            if 1 <= idx <= len(activas):
                reserva = activas[idx - 1]
            else:
                print("  ✘ Número inválido.")
                Consola.pausar()
                return
        except ValueError:
            print("  ✘ Debes ingresar un número válido.")
            Consola.pausar()
            return

        # Pide motivo de cancelación
        motivo = Consola.pedir("Motivo de cancelación (opcional)", obligatorio=False)
        if not motivo:
            motivo = "Sin especificar"

        # Cancela la reserva
        try:
            reserva.cancelar(motivo)
            print(f"\n  ⚠ RESERVA CANCELADA")
        except ErrorSistema as e:
            print(f"\n  ✘ Error al cancelar: {e}")

        Consola.pausar()

    def _procesar(self):
        """Procesa una reserva confirmada (marca como entregada y cobrada)."""
        Consola.subtitulo("PROCESAR RESERVA")

        # Obtiene solo las reservas confirmadas
        confirmadas = self._gestor.listar_por_estado(ESTADO_CONFIRMADA)

        if not confirmadas:
            print("  No hay reservas confirmadas para procesar.")
            Consola.pausar()
            return

        # Muestra las reservas confirmadas
        for i, r in enumerate(confirmadas, 1):
            print(f"  [{i}] ID: {r.id_reserva} | Cliente: {r.cliente.nombre}")

        try:
            idx = int(input("\n  Número de la reserva a procesar (0 para cancelar): ").strip())
            if idx == 0:
                return
            if 1 <= idx <= len(confirmadas):
                reserva = confirmadas[idx - 1]
            else:
                print("  ✘ Número inválido.")
                Consola.pausar()
                return
        except ValueError:
            print("  ✘ Debes ingresar un número válido.")
            Consola.pausar()
            return

        # Procesa la reserva (cambia estado a PROCESADA)
        try:
            resumen = reserva.procesar()
            print(f"\n  ✔ {resumen}")
        except ErrorSistema as e:
            print(f"\n  ✘ Error al procesar: {e}")

        Consola.pausar()

    def _listar_todas(self):
        """Muestra la lista completa de todas las reservas."""
        Consola.subtitulo("TODAS LAS RESERVAS")
        reservas = self._gestor.listar_todas()  # Obtiene todas las reservas

        if not reservas:
            print("  No hay reservas registradas.")
        else:
            print(f"  Total: {len(reservas)} reserva(s)\n")
            for r in reservas:  # Recorre y muestra cada reserva
                print(r.describir())
                print()
        Consola.pausar()

    def _listar_por_estado(self):
        """Filtra y muestra reservas por estado específico."""
        Consola.subtitulo("RESERVAS POR ESTADO")
        print("  Estados: pendiente | confirmada | cancelada | procesada")
        estado = Consola.pedir_opcion("Estado a filtrar", ["pendiente", "confirmada", "cancelada", "procesada"])
        reservas = self._gestor.listar_por_estado(estado.upper())  # Filtra por estado

        if not reservas:
            print(f"  No hay reservas en estado {estado.upper()}.")
        else:
            print(f"\n  {len(reservas)} reserva(s) en estado {estado.upper()}:\n")
            for r in reservas:
                print(r.describir())
                print()
        Consola.pausar()


# ─────────────────────────────────────────────
# CLASE PARA REPORTES
# ─────────────────────────────────────────────

class VistaReportes:
    """
    Clase que maneja la visualización de reportes y estadísticas.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES
    """

    def __init__(self, gestor_clientes: GestorClientes,
                 gestor_servicios: GestorServicios,
                 gestor_reservas: GestorReservas):
        """
        Constructor: recibe los tres gestores para obtener los datos.
        """
        self._gestor_clientes = gestor_clientes
        self._gestor_servicios = gestor_servicios
        self._gestor_reservas = gestor_reservas

    def mostrar(self):
        """Muestra los reportes y estadísticas del sistema."""
        Consola.titulo("REPORTES DEL SISTEMA")

        # Obtiene los datos de cada gestor
        total_clientes = self._gestor_clientes.total_clientes()
        total_servicios = self._gestor_servicios.total_servicios()
        total_reservas = self._gestor_reservas.total_reservas()
        ingresos = self._gestor_reservas.ingresos_totales()  # Suma de reservas procesadas

        # Muestra solo 4 líneas como se solicitó
        print(f"  Clientes registrados  : {total_clientes}")
        print(f"  Servicios en catálogo : {total_servicios}")
        print(f"  Reservas totales      : {total_reservas}")
        print(f"  Ingresos procesados   : ${ingresos:,.2f} COP")

        # Opción adicional para ver el log del sistema
        print()
        print("  ¿Ver el log del sistema?")
        resp = Consola.pedir_opcion("  (s/n)", ["s", "n"])
        if resp == "s":
            logger.mostrar_log(30)  # Muestra las últimas 30 líneas del log
        Consola.pausar()


# ─────────────────────────────────────────────
# CLASE PRINCIPAL DEL SISTEMA (MENÚ PRINCIPAL)
# ─────────────────────────────────────────────

class SistemaSoftwareFJ:
    """
    Clase principal que orquesta todo el sistema.
    Principios OOP: COMPOSICIÓN (tiene un objeto de cada vista)
    
    Esta clase es el corazón del programa. Crea los gestores, las vistas
    y ejecuta el menú principal.
    """

    def __init__(self):
        """Constructor del sistema. Inicializa gestores y vistas."""
        # Gestores (modelos) - manejan los datos y la lógica de negocio
        self._gestor_clientes = GestorClientes()
        self._gestor_servicios = GestorServicios()
        self._gestor_reservas = GestorReservas()

        # Vistas (controladores de interfaz) - manejan la interacción con el usuario
        self._vista_clientes = VistaClientes(self._gestor_clientes)
        self._vista_servicios = VistaServicios(self._gestor_servicios)
        self._vista_reservas = VistaReservas(
            self._gestor_reservas,
            self._gestor_clientes,
            self._gestor_servicios
        )
        self._vista_reportes = VistaReportes(
            self._gestor_clientes,
            self._gestor_servicios,
            self._gestor_reservas
        )

    def _ejecutar_simulacion(self):
        """Ejecuta la simulación automática de pruebas (11 operaciones)."""
        Consola.titulo("SIMULACIÓN AUTOMÁTICA")
        print("  Esto ejecutará 11 operaciones de prueba precargadas.")
        print("  Se usarán los gestores actuales de la sesión.")
        resp = Consola.pedir_opcion("¿Continuar? (s/n)", ["s", "n"])
        if resp == "s":
            # Llama a la simulación pasando los gestores actuales
            pruebas.ejecutar_simulacion_con_gestores(
                self._gestor_clientes,
                self._gestor_servicios,
                self._gestor_reservas
            )
        Consola.pausar()

    def _menu_principal(self):
        """Muestra el menú principal y procesa las opciones."""
        logger.iniciar_sesion()  # Registra el inicio de sesión en el log

        while True:  # Bucle infinito del menú principal
            Consola.titulo("SISTEMA SOFTWARE FJ")
            print("  Gestión de Clientes, Servicios y Reservas")
            print()
            print("  [1] Gestión de Clientes")
            print("  [2] Gestión de Servicios")
            print("  [3] Gestión de Reservas")
            print("  [4] Reportes y estadísticas")
            print("  [5] Ejecutar simulación automática (11 pruebas)")
            print("  [0] Salir")

            opcion = Consola.pedir_opcion("\nElige una opción", ["0", "1", "2", "3", "4", "5"])

            # Ejecuta la vista correspondiente según la opción
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
                print("\n  Sistema cerrado. Hasta pronto.")
                print(f"  El historial quedó guardado en: sistema.log\n")
                break  # Sale del bucle y termina el programa

    def iniciar(self):
        """Punto de entrada para ejecutar el sistema."""
        self._menu_principal()  # Llama al menú principal


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    """
    Esta es la primera línea que se ejecuta cuando corres:
    python main.py
    
    Crea una instancia de la clase principal y la inicia.
    """
    sistema = SistemaSoftwareFJ()  # Crea el objeto principal
    sistema.iniciar()  # Arranca el sistema
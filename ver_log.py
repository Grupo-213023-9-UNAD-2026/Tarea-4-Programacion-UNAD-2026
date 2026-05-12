"""
ver_log.py
Autor: Ezequiel Olmos Luque(Líder)
Curso: Programación 213023 - UNAD
==========
Herramienta de consola para inspeccionar el archivo `sistema.log`.
Permite ver el log completo, filtrar por nivel, buscar palabras,
revisar sesiones y consultar estadísticas básicas del sistema.
"""

# Importamos builtins para conservar una referencia estable al print original.
import builtins
# Importamos os para construir y consultar la ruta del archivo de log.
import os
# Importamos re para parsear líneas y buscar patrones dentro del log.
import re
# Importamos sys para detectar si la terminal soporta colores o no.
import sys
# Importamos Counter para contar niveles y acciones dentro del log.
from collections import Counter
# Importamos datetime para convertir fechas de texto a objetos reales.
from datetime import datetime
# Importamos anotaciones de tipos usadas en las clases del visor.
from typing import Any, Dict, List, Optional, Tuple


# Guardamos la función print original antes de hacer cualquier adaptación.
_PRINT_ORIGINAL = builtins.print


# Esta función convierte un texto a una versión segura para la consola.
def _normalizar_para_consola(texto: str, destino) -> str:
    # Detectamos la codificación configurada por el flujo de salida.
    encoding = getattr(destino, "encoding", None) or "utf-8"
    # Reconvertimos el texto y reemplazamos caracteres incompatibles.
    return texto.encode(encoding, errors="replace").decode(encoding, errors="replace")


# Esta función protege la salida para que Unicode no rompa la ejecución.
def _imprimir_seguro(*args, **kwargs) -> None:
    # Detectamos el destino de impresión o usamos stdout por defecto.
    destino = kwargs.get("file", sys.stdout)
    try:
        # Intentamos imprimir con el comportamiento normal primero.
        _PRINT_ORIGINAL(*args, **kwargs)
    except UnicodeEncodeError:
        # Si no es stdout o stderr, reenviamos el error real.
        if destino not in (sys.stdout, sys.stderr):
            raise
        # Recuperamos el separador configurado o usamos un espacio simple.
        separador = kwargs.get("sep", " ")
        # Recuperamos el terminador configurado o usamos salto de línea.
        fin = kwargs.get("end", "\n")
        # Recuperamos si se pidió vaciar el buffer al final.
        vaciar = kwargs.get("flush", False)
        # Convertimos todos los argumentos a una sola cadena de texto.
        texto = separador.join(str(arg) for arg in args)
        # Transformamos la cadena a un formato seguro para la consola.
        texto_seguro = _normalizar_para_consola(texto, destino)
        # Imprimimos la versión segura respetando end, file y flush.
        _PRINT_ORIGINAL(texto_seguro, end=fin, file=destino, flush=vaciar)


# Redefinimos print localmente para proteger todas las salidas del archivo.
print = _imprimir_seguro


# Esta clase centraliza constantes y rutas del visor de logs.
class Configuracion:
    """Configuración general del visor del archivo de log."""

    # Guardamos la carpeta donde vive este script.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Construimos la ruta absoluta del archivo `sistema.log`.
    ARCHIVO_LOG = os.path.join(BASE_DIR, "sistema.log")
    # Definimos colores ANSI opcionales para una mejor lectura en terminales compatibles.
    COLORES = {
        "INFO": "\033[92m",
        "ADVERTENCIA": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICO": "\033[95m",
        "TITULO": "\033[96m",
        "RESET": "\033[0m",
    }
    # Definimos la lista de niveles válidos conocidos por el sistema.
    NIVELES_VALIDOS = ["INFO", "ADVERTENCIA", "ERROR", "CRITICO"]
    # Definimos el patrón base para extraer fecha, nivel y mensaje.
    PATRON_LOG = r"\[(.*?)\]\s*\[(.*?)\]\s*(.*)"


# Esta clase encapsula la aplicación opcional de colores ANSI.
class ManejadorColores:
    """Aplica color solo cuando la terminal realmente lo soporta."""

    def __init__(self, usar_colores: bool = True):
        # Activamos colores solo si el usuario lo pidió y la terminal lo soporta.
        self._usar_colores = usar_colores and self._soporta_colores()

    @staticmethod
    def _soporta_colores() -> bool:
        # Verificamos que stdout exista y sea una terminal interactiva.
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def aplicar(self, texto: str, clave_color: str) -> str:
        # Si el visor no usará colores, devolvemos el texto sin cambios.
        if not self._usar_colores:
            return texto
        # Tomamos el código ANSI asociado a la clave solicitada.
        color = Configuracion.COLORES.get(clave_color, "")
        # Tomamos el código de reseteo para cerrar el color aplicado.
        reset = Configuracion.COLORES["RESET"]
        # Envolvemos el texto con el color indicado.
        return f"{color}{texto}{reset}"


# Esta clase convierte líneas de log en estructuras más fáciles de procesar.
class ParseadorLog:
    """Parsea cada línea del archivo `sistema.log`."""

    @classmethod
    def parsear_linea(cls, linea: str) -> Tuple[Optional[datetime], Optional[str], str]:
        # Intentamos hacer coincidir la línea con el patrón del log.
        coincidencia = re.match(Configuracion.PATRON_LOG, linea)
        # Si la línea no coincide, la tratamos como texto libre.
        if not coincidencia:
            return None, None, linea.strip()
        # Extraemos la fecha, el nivel y el mensaje desde la coincidencia.
        fecha_str, nivel, mensaje = coincidencia.groups()
        try:
            # Convertimos el texto de fecha a un objeto datetime real.
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Si la fecha no se pudo interpretar, devolvemos None en ese campo.
            fecha = None
        # Devolvemos la tupla normalizada para uso posterior.
        return fecha, nivel, mensaje.strip()


# Esta clase maneja las operaciones de lectura del archivo de log.
class LectorLog:
    """Lee el archivo `sistema.log` desde disco."""

    def __init__(self, ruta_archivo: str | None = None):
        # Guardamos la ruta configurada o la predeterminada del proyecto.
        self._ruta = ruta_archivo or Configuracion.ARCHIVO_LOG

    @property
    def ruta(self) -> str:
        # Exponemos la ruta del archivo para mostrarla en estadísticas.
        return self._ruta

    def existe(self) -> bool:
        # Indicamos si el archivo ya está presente en disco.
        return os.path.exists(self._ruta)

    def leer_todas(self) -> Optional[List[str]]:
        # Si el archivo todavía no existe, devolvemos None.
        if not self.existe():
            return None
        try:
            # Abrimos el archivo en modo lectura usando UTF-8.
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                # Devolvemos todas las líneas tal como están almacenadas.
                return archivo.readlines()
        except OSError as error:
            # Informamos el error sin lanzar una excepción técnica hacia arriba.
            print(f"[ERROR] No se pudo leer el archivo de log: {error}")
            # Devolvemos None para indicar que hubo un problema.
            return None


# Esta clase calcula estadísticas y filtros a partir del log leído.
class EstadisticasLog:
    """Analiza el contenido del archivo de log."""

    def __init__(self, lector: LectorLog):
        # Guardamos el lector para recuperar las líneas cuando haga falta.
        self._lector = lector
        # Inicializamos el caché de líneas completas sin cargar nada aún.
        self._lineas: Optional[List[str]] = None
        # Inicializamos el caché de líneas parseadas.
        self._datos_parseados: Optional[List[Tuple[str, Optional[datetime], Optional[str], str]]] = None

    def _cargar_datos(self) -> None:
        # Si las líneas aún no fueron cargadas, las leemos del archivo.
        if self._lineas is None:
            self._lineas = self._lector.leer_todas()
        # Si los datos parseados aún no existen, los construimos.
        if self._datos_parseados is None:
            self._datos_parseados = []
            # Solo iteramos si sí hay líneas disponibles.
            if self._lineas:
                for linea in self._lineas:
                    # Parseamos la línea actual a fecha, nivel y mensaje.
                    fecha, nivel, mensaje = ParseadorLog.parsear_linea(linea)
                    # Guardamos tanto la línea cruda como los campos derivados.
                    self._datos_parseados.append((linea, fecha, nivel, mensaje))

    def total_lineas(self) -> int:
        # Nos aseguramos de que el caché esté cargado antes de contar.
        self._cargar_datos()
        # Retornamos cero si no existen líneas o su cantidad real en caso contrario.
        return len(self._lineas) if self._lineas else 0

    def total_dias(self) -> int:
        # Nos aseguramos de que el caché esté cargado antes de calcular.
        self._cargar_datos()
        # Si no hay datos parseados, no existen días registrados.
        if not self._datos_parseados:
            return 0
        # Creamos un conjunto para quedarnos solo con fechas únicas.
        dias = {fecha.date() for _, fecha, _, _ in self._datos_parseados if fecha}
        # Devolvemos el total de días distintos encontrados.
        return len(dias)

    def conteo_por_nivel(self) -> Dict[str, int]:
        # Nos aseguramos de que el caché esté cargado antes de contar.
        self._cargar_datos()
        # Creamos un contador vacío para acumular niveles.
        contador = Counter()
        # Recorremos cada dato parseado buscando el nivel del log.
        for _, _, nivel, _ in self._datos_parseados or []:
            # Si la línea tiene nivel reconocido, sumamos uno.
            if nivel:
                contador[nivel] += 1
        # Convertimos el Counter a un diccionario simple.
        return dict(contador)

    def conteo_acciones(self) -> Dict[str, int]:
        # Nos aseguramos de que el caché esté cargado antes de analizar mensajes.
        self._cargar_datos()
        # Inicializamos un diccionario con las acciones que queremos medir.
        acciones = {
            "registrado": 0,
            "confirmada": 0,
            "cancelada": 0,
            "procesada": 0,
            "error": 0,
            "advertencia": 0,
        }
        # Recorremos cada mensaje parseado para buscar palabras clave.
        for _, _, _, mensaje in self._datos_parseados or []:
            # Convertimos el mensaje a minúsculas para comparar sin sesgo.
            mensaje_min = mensaje.lower()
            # Contamos registros de clientes u objetos creados.
            if "registrado" in mensaje_min:
                acciones["registrado"] += 1
            # Contamos confirmaciones de reservas.
            if "confirmada" in mensaje_min:
                acciones["confirmada"] += 1
            # Contamos cancelaciones de reservas.
            if "cancelada" in mensaje_min:
                acciones["cancelada"] += 1
            # Contamos reservas procesadas.
            if "procesada" in mensaje_min:
                acciones["procesada"] += 1
            # Contamos mensajes con la palabra error.
            if "error" in mensaje_min:
                acciones["error"] += 1
            # Contamos mensajes con la palabra advertencia o warning.
            if "advertencia" in mensaje_min or "warning" in mensaje_min:
                acciones["advertencia"] += 1
        # Devolvemos el resumen de conteos encontrado.
        return acciones

    def filtrar_por_nivel(self, nivel: str) -> List[str]:
        # Nos aseguramos de que el caché esté cargado antes de filtrar.
        self._cargar_datos()
        # Normalizamos el nivel solicitado a mayúsculas.
        nivel_buscado = nivel.strip().upper()
        # Retornamos solo las líneas cuyo nivel coincide.
        return [
            linea
            for linea, _, nivel_log, _ in self._datos_parseados or []
            if nivel_log == nivel_buscado
        ]

    def filtrar_por_palabra(self, palabra: str) -> List[str]:
        # Nos aseguramos de que el caché esté cargado antes de filtrar.
        self._cargar_datos()
        # Si no hay líneas cargadas, devolvemos una lista vacía.
        if not self._lineas:
            return []
        # Normalizamos la palabra a minúsculas para comparar de forma insensible.
        palabra_buscada = palabra.lower()
        # Retornamos solo las líneas que contengan la palabra o frase solicitada.
        return [linea for linea in self._lineas if palabra_buscada in linea.lower()]

    def filtrar_por_rango_fechas(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[str]:
        # Nos aseguramos de que el caché esté cargado antes de filtrar.
        self._cargar_datos()
        # Ajustamos la fecha final para cubrir hasta el último segundo del día.
        fecha_fin_ajustada = fecha_fin.replace(hour=23, minute=59, second=59)
        # Retornamos solo las líneas con fecha dentro del rango solicitado.
        return [
            linea
            for linea, fecha, _, _ in self._datos_parseados or []
            if fecha and fecha_inicio <= fecha <= fecha_fin_ajustada
        ]

    def obtener_sesiones(self) -> List[str]:
        # Nos aseguramos de que el caché esté cargado antes de buscar sesiones.
        self._cargar_datos()
        # Si no hay líneas disponibles, devolvemos lista vacía.
        if not self._lineas:
            return []
        # Inicializamos la lista de sesiones encontradas.
        sesiones = []
        # Recorremos línea a línea buscando el marcador de inicio.
        for linea in self._lineas:
            # Solo nos interesan las líneas que mencionan sesión iniciada.
            if "SESION INICIADA" in linea or "SESIÓN INICIADA" in linea:
                # Intentamos extraer el texto posterior a los dos puntos.
                coincidencia = re.search(r"SESI[ÓO]N INICIADA: (.*)", linea)
                # Si encontramos fecha legible, guardamos solo ese fragmento.
                if coincidencia:
                    sesiones.append(coincidencia.group(1).strip())
                else:
                    # Si no, guardamos la línea completa como respaldo.
                    sesiones.append(linea.strip())
        # Devolvemos la lista final de sesiones detectadas.
        return sesiones


# Esta clase se encarga de presentar líneas y mensajes al usuario.
class VisorLog:
    """Formatea la salida del visor de logs."""

    def __init__(self, colores: ManejadorColores):
        # Guardamos el manejador de colores para embellecer la salida.
        self._colores = colores

    def mostrar_linea(self, linea: str) -> None:
        # Parseamos la línea para decidir cómo mostrarla.
        fecha, nivel, mensaje = ParseadorLog.parsear_linea(linea)
        # Si la línea no tiene fecha ni nivel, la mostramos como texto simple.
        if fecha is None or nivel is None:
            print(linea.rstrip())
            return
        # Formateamos la fecha como texto legible.
        fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")
        # Aplicamos color al bloque de fecha si el visor lo permite.
        fecha_coloreada = self._colores.aplicar(fecha_str, "TITULO")
        # Aplicamos color al nivel usando la clave de su nombre.
        nivel_coloreado = self._colores.aplicar(f"[{nivel}]", nivel)
        # Mostramos la línea completa con fecha, nivel y mensaje.
        print(f"{fecha_coloreada} {nivel_coloreado} {mensaje}")

    def mostrar_lista(self, lineas: List[str], titulo: str | None = None) -> None:
        # Si llega un título, lo mostramos antes del bloque de líneas.
        if titulo:
            print("\n" + "=" * 60)
            print(titulo)
            print("=" * 60)
        # Mostramos una por una todas las líneas recibidas.
        for linea in lineas:
            self.mostrar_linea(linea)
        # Si se mostraron líneas, añadimos un contador final.
        if lineas:
            print(f"\nTotal de lineas mostradas: {len(lineas)}\n")

    def mostrar_error(self, mensaje: str) -> None:
        # Mostramos un mensaje de error uniforme para el visor.
        print(f"[ERROR] {mensaje}")

    def mostrar_info(self, mensaje: str) -> None:
        # Mostramos un mensaje informativo uniforme para el visor.
        print(f"[INFO] {mensaje}")


# Esta clase implementa el menú interactivo del visor de logs.
class MenuLog:
    """Controla la navegación del usuario dentro del visor."""

    def __init__(self, lector: LectorLog, estadisticas: EstadisticasLog, visor: VisorLog):
        # Guardamos el lector para acceder al archivo.
        self._lector = lector
        # Guardamos el analizador de estadísticas y filtros.
        self._estadisticas = estadisticas
        # Guardamos el visor que presentará la salida en consola.
        self._visor = visor

    def _mostrar_encabezado(self) -> None:
        # Mostramos un encabezado simple del visor de logs.
        print("\n" + "=" * 60)
        print("VISOR DEL SISTEMA DE LOGS - SOFTWARE FJ")
        print("=" * 60)

    def _mostrar_opciones(self) -> None:
        # Mostramos todas las acciones disponibles del menú.
        print("[1] Ver todo el log")
        print("[2] Ver ultimas N lineas")
        print("[3] Ver solo errores y criticos")
        print("[4] Ver solo advertencias")
        print("[5] Ver solo informacion")
        print("[6] Buscar por palabra clave")
        print("[7] Ver por rango de fechas")
        print("[8] Estadisticas del log")
        print("[9] Ver sesiones del sistema")
        print("[0] Salir")
        print("-" * 60)

    def _verificar_archivo(self) -> bool:
        # Si el archivo no existe, informamos cómo generarlo.
        if not self._lector.existe():
            print(f"[WARN] El archivo '{self._lector.ruta}' aun no existe.")
            print("Ejecuta primero alguno de estos archivos para generarlo:")
            print("  python main.py")
            print("  python pruebas.py")
            return False
        # Si el archivo existe, devolvemos True para continuar normalmente.
        return True

    def _opcion_ver_todo(self) -> None:
        # Leemos todas las líneas del archivo actual.
        lineas = self._lector.leer_todas() or []
        # Mostramos la lista completa con título descriptivo.
        self._visor.mostrar_lista(lineas, "LOG COMPLETO")

    def _opcion_ver_ultimas_n(self) -> None:
        # Leemos todas las líneas del archivo actual.
        lineas = self._lector.leer_todas() or []
        # Si el archivo no tiene líneas, salimos sin mostrar nada.
        if not lineas:
            return
        try:
            # Pedimos cuántas líneas quiere ver el usuario.
            cantidad = int(input("Cuantas lineas quieres ver? (default 20): ").strip() or "20")
        except ValueError:
            # Si el dato no es válido, usamos 20 como valor de respaldo.
            cantidad = 20
        # Tomamos las últimas N líneas disponibles.
        ultimas = lineas[-cantidad:] if len(lineas) >= cantidad else lineas
        # Mostramos el subconjunto solicitado.
        self._visor.mostrar_lista(ultimas, f"ULTIMAS {len(ultimas)} LINEAS")

    def _opcion_ver_errores_criticos(self) -> None:
        # Filtramos primero las líneas de error.
        errores = self._estadisticas.filtrar_por_nivel("ERROR")
        # Filtramos luego las líneas críticas.
        criticos = self._estadisticas.filtrar_por_nivel("CRITICO")
        # Mostramos ambas colecciones por separado.
        self._visor.mostrar_lista(errores, "REGISTROS [ERROR]")
        self._visor.mostrar_lista(criticos, "REGISTROS [CRITICO]")

    def _opcion_ver_advertencias(self) -> None:
        # Filtramos el log para quedarnos solo con advertencias.
        lineas = self._estadisticas.filtrar_por_nivel("ADVERTENCIA")
        # Mostramos el resultado al usuario.
        self._visor.mostrar_lista(lineas, "REGISTROS [ADVERTENCIA]")

    def _opcion_ver_info(self) -> None:
        # Filtramos el log para quedarnos solo con eventos informativos.
        lineas = self._estadisticas.filtrar_por_nivel("INFO")
        # Mostramos el resultado al usuario.
        self._visor.mostrar_lista(lineas, "REGISTROS [INFO]")

    def _opcion_buscar_palabra(self) -> None:
        # Pedimos la palabra o frase a buscar.
        palabra = input("Palabra o frase a buscar: ").strip()
        # Si el usuario no escribió nada, informamos y salimos.
        if not palabra:
            self._visor.mostrar_info("No ingresaste ninguna palabra para buscar.")
            return
        # Filtramos las líneas que contienen la palabra solicitada.
        lineas = self._estadisticas.filtrar_por_palabra(palabra)
        # Mostramos los resultados encontrados.
        self._visor.mostrar_lista(lineas, f"BUSQUEDA: '{palabra}'")

    def _opcion_ver_por_fecha(self) -> None:
        # Pedimos la fecha inicial del rango.
        fecha_inicio_str = input("Fecha inicial (YYYY-MM-DD): ").strip()
        # Pedimos la fecha final del rango.
        fecha_fin_str = input("Fecha final (YYYY-MM-DD): ").strip()
        try:
            # Convertimos la fecha inicial a datetime.
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            # Convertimos la fecha final a datetime.
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
        except ValueError:
            # Si el formato no es válido, mostramos el error y salimos.
            self._visor.mostrar_error("Formato invalido. Usa YYYY-MM-DD.")
            return
        # Filtramos las líneas que caen dentro del rango.
        lineas = self._estadisticas.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        # Mostramos los resultados encontrados.
        self._visor.mostrar_lista(
            lineas,
            f"RANGO: {fecha_inicio_str} -> {fecha_fin_str}",
        )

    def _opcion_mostrar_estadisticas(self) -> None:
        # Calculamos el número total de líneas del archivo.
        total_lineas = self._estadisticas.total_lineas()
        # Calculamos cuántos días distintos tienen registros.
        total_dias = self._estadisticas.total_dias()
        # Recuperamos el conteo de eventos por nivel.
        conteo_niveles = self._estadisticas.conteo_por_nivel()
        # Recuperamos el conteo aproximado de acciones clave.
        acciones = self._estadisticas.conteo_acciones()
        # Mostramos un encabezado para la sección de estadísticas.
        print("\n" + "=" * 60)
        print("ESTADISTICAS DEL SISTEMA DE LOGS")
        print("=" * 60)
        # Mostramos la ruta del archivo inspeccionado.
        print(f"Archivo        : {self._lector.ruta}")
        # Mostramos el total de líneas leídas.
        print(f"Lineas totales : {total_lineas}")
        # Mostramos el número de días con actividad.
        print(f"Dias con logs  : {total_dias}")
        # Mostramos el conteo resumido por nivel de severidad.
        print("\nPor nivel:")
        for nivel in Configuracion.NIVELES_VALIDOS:
            print(f"  {nivel:<12}: {conteo_niveles.get(nivel, 0)}")
        # Mostramos el conteo resumido de acciones clave detectadas.
        print("\nAcciones registradas:")
        print(f"  Registrado   : {acciones['registrado']}")
        print(f"  Confirmada   : {acciones['confirmada']}")
        print(f"  Cancelada    : {acciones['cancelada']}")
        print(f"  Procesada    : {acciones['procesada']}")
        print(f"  Error        : {acciones['error']}")
        print(f"  Advertencia  : {acciones['advertencia']}")
        print("=" * 60 + "\n")

    def _opcion_ver_sesiones(self) -> None:
        # Recuperamos la lista de sesiones detectadas dentro del log.
        sesiones = self._estadisticas.obtener_sesiones()
        # Mostramos el encabezado de la sección.
        print("\n" + "=" * 60)
        print(f"SESIONES DEL SISTEMA (Total: {len(sesiones)})")
        print("=" * 60)
        # Recorremos y listamos cada sesión encontrada.
        for indice, sesion in enumerate(sesiones, start=1):
            print(f"{indice}. {sesion}")
        # Si no hubo sesiones, lo indicamos explícitamente.
        if not sesiones:
            print("No hay sesiones registradas aun.")
        print()

    def ejecutar(self) -> None:
        # Mostramos la advertencia inicial si el archivo aún no existe.
        self._verificar_archivo()
        # Mantenemos activo el menú hasta que el usuario decida salir.
        while True:
            # Mostramos el encabezado principal del visor.
            self._mostrar_encabezado()
            # Mostramos todas las opciones disponibles del menú.
            self._mostrar_opciones()
            # Pedimos la opción elegida por el usuario.
            opcion = input("Elige una opcion: ").strip()
            # Relacionamos opciones con sus métodos correspondientes.
            acciones = {
                "1": self._opcion_ver_todo,
                "2": self._opcion_ver_ultimas_n,
                "3": self._opcion_ver_errores_criticos,
                "4": self._opcion_ver_advertencias,
                "5": self._opcion_ver_info,
                "6": self._opcion_buscar_palabra,
                "7": self._opcion_ver_por_fecha,
                "8": self._opcion_mostrar_estadisticas,
                "9": self._opcion_ver_sesiones,
            }
            # Si la opción existe, ejecutamos la acción asociada.
            if opcion in acciones:
                acciones[opcion]()
            elif opcion == "0":
                # Si el usuario eligió salir, cerramos el menú.
                print("\nHasta luego.\n")
                break
            else:
                # Si la opción no existe, lo indicamos y repetimos el ciclo.
                print("[WARN] Opcion invalida. Intenta de nuevo.\n")

    def ejecutar_simple(self, opcion: str) -> None:
        # Mostramos la advertencia inicial si el archivo aún no existe.
        self._verificar_archivo()
        # Construimos el mismo despacho usado en el menú interactivo.
        acciones = {
            "1": self._opcion_ver_todo,
            "2": self._opcion_ver_ultimas_n,
            "3": self._opcion_ver_errores_criticos,
            "4": self._opcion_ver_advertencias,
            "5": self._opcion_ver_info,
            "6": self._opcion_buscar_palabra,
            "7": self._opcion_ver_por_fecha,
            "8": self._opcion_mostrar_estadisticas,
            "9": self._opcion_ver_sesiones,
        }
        # Si la opción existe, ejecutamos la acción solicitada.
        if opcion in acciones:
            acciones[opcion]()
        else:
            # Si no existe, informamos la invalidez del código recibido.
            print(f"[WARN] La opcion '{opcion}' no es valida.")


# Esta clase une lector, estadísticas, visor y menú en una sola interfaz.
class VisorLogSistema:
    """Clase principal del visor de logs del proyecto."""

    def __init__(self, usar_colores: bool = True):
        # Creamos el manejador de colores opcional para la salida.
        self._colores = ManejadorColores(usar_colores=usar_colores)
        # Creamos el lector del archivo de log.
        self._lector = LectorLog()
        # Creamos el analizador estadístico del contenido leído.
        self._estadisticas = EstadisticasLog(self._lector)
        # Creamos el componente visual que imprimirá resultados.
        self._visor = VisorLog(self._colores)
        # Creamos el menú interactivo que orquesta las opciones disponibles.
        self._menu = MenuLog(self._lector, self._estadisticas, self._visor)

    def iniciar(self) -> None:
        # Iniciamos el bucle interactivo del menú principal.
        self._menu.ejecutar()

    def ejecutar_opcion(self, opcion: str) -> None:
        # Ejecutamos una opción concreta sin mostrar el menú completo.
        self._menu.ejecutar_simple(opcion)

    def mostrar_ultimas(self, cantidad: int = 20) -> None:
        # Leemos todas las líneas del archivo actual.
        lineas = self._lector.leer_todas() or []
        # Tomamos las últimas N líneas solicitadas.
        ultimas = lineas[-cantidad:] if len(lineas) >= cantidad else lineas
        # Mostramos el subconjunto resultante.
        self._visor.mostrar_lista(ultimas, f"ULTIMAS {len(ultimas)} LINEAS")

    def buscar(self, palabra: str) -> None:
        # Filtramos el log por la palabra o frase indicada.
        lineas = self._estadisticas.filtrar_por_palabra(palabra)
        # Mostramos la lista resultante.
        self._visor.mostrar_lista(lineas, f"BUSQUEDA: '{palabra}'")

    def estadisticas(self) -> Dict[str, Any]:
        # Devolvemos un diccionario con métricas clave del archivo.
        return {
            "total_lineas": self._estadisticas.total_lineas(),
            "total_dias": self._estadisticas.total_dias(),
            "conteo_por_nivel": self._estadisticas.conteo_por_nivel(),
            "acciones": self._estadisticas.conteo_acciones(),
            "sesiones": self._estadisticas.obtener_sesiones(),
        }


# Esta función sirve como entrada simple para ejecutar el visor directamente.
def main() -> None:
    # Creamos la instancia principal del visor de logs.
    visor = VisorLogSistema(usar_colores=True)
    # Iniciamos el menú interactivo del visor.
    visor.iniciar()


# Este bloque permite ejecutar el visor desde la consola.
if __name__ == "__main__":
    # Lanzamos la función principal del visor.
    main()

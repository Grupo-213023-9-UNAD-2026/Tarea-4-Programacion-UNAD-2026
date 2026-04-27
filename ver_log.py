"""
ver_log.py
==========
Herramienta independiente para visualizar el archivo sistema.log
Permite ver todo el log, filtrar por nivel, buscar palabras clave,
y mostrar estadísticas del sistema.

VERSIÓN REFACTORIZADA CON CLASES (POO)

Ejecución: python ver_log.py

Autor: Ezequiel Olmos Luque (Líder)
Curso: Programación 213023 - UNAD
"""

import os
import re
import sys
import builtins
from datetime import datetime
from collections import Counter
from typing import List, Tuple, Optional, Dict, Any


def _imprimir_seguro(*args, **kwargs) -> None:
    """
    Imprime en consola sin fallar cuando la terminal no soporta algunos
    caracteres Unicode (caso comun en Windows con codificacion cp1252).
    """
    destino = kwargs.get("file", sys.stdout)

    try:
        builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        if destino not in (sys.stdout, sys.stderr):
            raise

        separador = kwargs.get("sep", " ")
        fin = kwargs.get("end", "\n")
        vaciar = kwargs.get("flush", False)

        texto = separador.join(str(arg) for arg in args)
        encoding = getattr(destino, "encoding", None) or "utf-8"
        texto_seguro = texto.encode(encoding, errors="replace").decode(encoding, errors="replace")

        builtins.print(texto_seguro, end=fin, file=destino, flush=vaciar)


print = _imprimir_seguro


# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────

class Configuracion:
    """
    Clase que centraliza la configuración del visor de logs.
    Principio OOP: ENCAPSULACIÓN de constantes.
    """
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ARCHIVO_LOG = os.path.join(BASE_DIR, "sistema.log")
    
    # Colores ANSI para mejorar la visualización en consola
    COLORES = {
        'INFO': '\033[92m',       # Verde
        'ADVERTENCIA': '\033[93m', # Amarillo
        'ERROR': '\033[91m',       # Rojo
        'CRITICO': '\033[95m',     # Magenta
        'RESET': '\033[0m',        # Reset
        'CYAN': '\033[96m',        # Cyan
        'BLUE': '\033[94m'         # Azul
    }
    
    # Niveles de log válidos
    NIVELES_VALIDOS = ["INFO", "ADVERTENCIA", "ERROR", "CRITICO"]
    
    # Estados para el menú
    ESTADOS_MENU = {
        "1": "ver_todo",
        "2": "ver_ultimas_n",
        "3": "ver_errores_criticos",
        "4": "ver_advertencias",
        "5": "ver_info",
        "6": "buscar_palabra",
        "7": "ver_por_fecha",
        "8": "mostrar_estadisticas",
        "9": "ver_sesiones",
        "0": "salir"
    }


# ─────────────────────────────────────────────
# CLASE PARA MANEJO DE COLORES
# ─────────────────────────────────────────────

class ManejadorColores:
    """
    Clase que maneja la aplicación de colores a la salida de consola.
    Principio OOP: ENCAPSULACIÓN de la lógica de colores.
    """
    
    def __init__(self, usar_colores: bool = True):
        """
        Constructor del manejador de colores.
        
        Parámetros:
            usar_colores (bool): Si se deben aplicar colores (por defecto True)
        """
        self._usar_colores = usar_colores and self._soporta_colores()
    
    @staticmethod
    def _soporta_colores() -> bool:
        """Verifica si la terminal soporta colores ANSI."""
        return hasattr(sys, 'stdout') and sys.stdout.isatty()
    
    def aplicar(self, texto: str, color: str) -> str:
        """
        Aplica color al texto si está habilitado.
        
        Parámetros:
            texto (str): El texto a colorear
            color (str): El nombre del color (INFO, ADVERTENCIA, ERROR, CRITICO, CYAN, BLUE)
        
        Retorna:
            str: Texto con códigos de color ANSI o texto sin formato
        """
        if not self._usar_colores:
            return texto
        
        codigo_color = Configuracion.COLORES.get(color, "")
        reset = Configuracion.COLORES.get("RESET", "")
        
        return f"{codigo_color}{texto}{reset}"
    
    def info(self, texto: str) -> str:
        """Aplica color verde (para nivel INFO)."""
        return self.aplicar(texto, "INFO")
    
    def advertencia(self, texto: str) -> str:
        """Aplica color amarillo (para nivel ADVERTENCIA)."""
        return self.aplicar(texto, "ADVERTENCIA")
    
    def error(self, texto: str) -> str:
        """Aplica color rojo (para nivel ERROR)."""
        return self.aplicar(texto, "ERROR")
    
    def critico(self, texto: str) -> str:
        """Aplica color magenta (para nivel CRITICO)."""
        return self.aplicar(texto, "CRITICO")
    
    def cyan(self, texto: str) -> str:
        """Aplica color cyan (para fechas)."""
        return self.aplicar(texto, "CYAN")
    
    def blue(self, texto: str) -> str:
        """Aplica color azul (para títulos)."""
        return self.aplicar(texto, "BLUE")


# ─────────────────────────────────────────────
# CLASE PARA PARSING DE LÍNEAS DE LOG
# ─────────────────────────────────────────────

class ParseadorLog:
    """
    Clase que parsea líneas del archivo de log.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES.
    """
    
    # Patrón regex para parsear líneas de log
    PATRON_LOG = r'\[(.*?)\]\s*\[(.*?)\]\s*(.*)'
    
    @classmethod
    def parsear_linea(cls, linea: str) -> Tuple[Optional[datetime], Optional[str], str]:
        """
        Parsea una línea del log y devuelve (fecha, nivel, mensaje).
        
        Parámetros:
            linea (str): Línea del archivo de log
        
        Retorna:
            Tuple: (fecha, nivel, mensaje) - fecha puede ser None si no es línea válida
        """
        coincidencia = re.match(cls.PATRON_LOG, linea)
        
        if coincidencia:
            fecha_str, nivel, mensaje = coincidencia.groups()
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                fecha = None
            return fecha, nivel, mensaje.strip()
        
        return None, None, linea.strip()


# ─────────────────────────────────────────────
# CLASE PARA LECTURA DEL ARCHIVO DE LOG
# ─────────────────────────────────────────────

class LectorLog:
    """
    Clase que maneja la lectura del archivo de log.
    Principio OOP: ENCAPSULACIÓN de operaciones de archivo.
    """
    
    def __init__(self, ruta_archivo: str = None):
        """
        Constructor del lector de log.
        
        Parámetros:
            ruta_archivo (str): Ruta al archivo de log (por defecto usa Configuracion.ARCHIVO_LOG)
        """
        self._ruta = ruta_archivo or Configuracion.ARCHIVO_LOG
    
    @property
    def ruta(self) -> str:
        """Getter de la ruta del archivo de log."""
        return self._ruta
    
    def existe(self) -> bool:
        """Verifica si el archivo de log existe."""
        return os.path.exists(self._ruta)
    
    def leer_todas(self) -> Optional[List[str]]:
        """
        Lee todas las líneas del archivo de log.
        
        Retorna:
            List[str] | None: Lista de líneas o None si hay error
        """
        if not self.existe():
            return None
        
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                return archivo.readlines()
        except Exception as e:
            print(f"\n  ✘ Error al leer el archivo: {e}\n")
            return None
    
    def obtener_lineas_validas(self) -> List[Tuple[Optional[datetime], Optional[str], str]]:
        """
        Lee el archivo y parsea cada línea.
        
        Retorna:
            List[Tuple]: Lista de tuplas (fecha, nivel, mensaje) para líneas válidas
        """
        lineas = self.leer_todas()
        if not lineas:
            return []
        
        resultados = []
        for linea in lineas:
            fecha, nivel, mensaje = ParseadorLog.parsear_linea(linea)
            if fecha is not None or nivel is not None:
                resultados.append((fecha, nivel, mensaje))
        
        return resultados


# ─────────────────────────────────────────────
# CLASE PARA ESTADÍSTICAS DEL LOG
# ─────────────────────────────────────────────

class EstadisticasLog:
    """
    Clase que calcula estadísticas a partir del archivo de log.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES.
    """
    
    def __init__(self, lector: LectorLog):
        """
        Constructor de estadísticas.
        
        Parámetros:
            lector (LectorLog): Instancia del lector de log
        """
        self._lector = lector
        self._lineas = None
        self._datos_parseados = None
    
    def _cargar_datos(self) -> None:
        """Carga y parsea los datos del log (caché interno)."""
        if self._lineas is None:
            self._lineas = self._lector.leer_todas()
        
        if self._datos_parseados is None:
            self._datos_parseados = []
            if self._lineas:
                for linea in self._lineas:
                    fecha, nivel, mensaje = ParseadorLog.parsear_linea(linea)
                    if fecha is not None or nivel is not None:
                        self._datos_parseados.append((linea, fecha, nivel, mensaje))
    
    def total_lineas(self) -> int:
        """Retorna el número total de líneas en el log."""
        self._cargar_datos()
        return len(self._lineas) if self._lineas else 0
    
    def total_dias(self) -> int:
        """Retorna el número de días únicos con registros."""
        self._cargar_datos()
        if not self._datos_parseados:
            return 0
        
        fechas = set()
        for _, fecha, _, _ in self._datos_parseados:
            if fecha:
                fechas.add(fecha.date())
        
        return len(fechas)
    
    def conteo_por_nivel(self) -> Dict[str, int]:
        """Retorna un diccionario con el conteo de registros por nivel."""
        self._cargar_datos()
        
        contador = Counter()
        for _, _, nivel, _ in self._datos_parseados:
            if nivel:
                contador[nivel] += 1
        
        return dict(contador)
    
    def conteo_acciones(self) -> Dict[str, int]:
        """
        Retorna un diccionario con el conteo de acciones específicas.
        Acciones: registrado, confirmada, cancelada, procesada, error, advertencia
        """
        self._cargar_datos()
        
        acciones = {
            "registrado": 0,
            "confirmada": 0,
            "cancelada": 0,
            "procesada": 0,
            "error": 0,
            "advertencia": 0
        }
        
        for _, _, _, mensaje in self._datos_parseados:
            mensaje_lower = mensaje.lower()
            
            if "registrado" in mensaje_lower:
                acciones["registrado"] += 1
            if "confirmada" in mensaje_lower:
                acciones["confirmada"] += 1
            if "cancelada" in mensaje_lower:
                acciones["cancelada"] += 1
            if "procesada" in mensaje_lower:
                acciones["procesada"] += 1
            if "error" in mensaje_lower:
                acciones["error"] += 1
            if "advertencia" in mensaje_lower or "warning" in mensaje_lower:
                acciones["advertencia"] += 1
        
        return acciones
    
    def filtrar_por_nivel(self, nivel: str) -> List[str]:
        """
        Filtra y retorna líneas de un nivel específico.
        
        Parámetros:
            nivel (str): Nivel a filtrar (INFO, ADVERTENCIA, ERROR, CRITICO)
        
        Retorna:
            List[str]: Lista de líneas que coinciden con el nivel
        """
        self._cargar_datos()
        
        if not self._lineas:
            return []
        
        nivel_buscar = nivel.upper()
        return [
            linea
            for linea, _, nivel_log, _ in self._datos_parseados
            if nivel_log == nivel_buscar
        ]
    
    def filtrar_por_palabra(self, palabra: str) -> List[str]:
        """
        Filtra y retorna líneas que contienen una palabra clave.
        
        Parámetros:
            palabra (str): Palabra o frase a buscar
        
        Retorna:
            List[str]: Lista de líneas que contienen la palabra
        """
        self._cargar_datos()
        
        if not self._lineas:
            return []
        
        palabra_lower = palabra.lower()
        return [linea for linea in self._lineas if palabra_lower in linea.lower()]
    
    def filtrar_por_rango_fechas(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[str]:
        """
        Filtra y retorna líneas dentro de un rango de fechas.
        
        Parámetros:
            fecha_inicio (datetime): Fecha inicial del rango
            fecha_fin (datetime): Fecha final del rango
        
        Retorna:
            List[str]: Lista de líneas dentro del rango
        """
        self._cargar_datos()
        
        if not self._lineas:
            return []
        
        # Ajustar fecha_fin para incluir todo el día
        fecha_fin_ajustada = fecha_fin.replace(hour=23, minute=59, second=59)
        
        return [
            linea
            for linea, fecha, _, _ in self._datos_parseados
            if fecha and fecha_inicio <= fecha <= fecha_fin_ajustada
        ]
    
    def obtener_sesiones(self) -> List[str]:
        """Extrae y retorna las líneas que marcan inicio de sesión."""
        self._cargar_datos()
        
        if not self._lineas:
            return []
        
        sesiones = []
        for i, linea in enumerate(self._lineas):
            if "SESIÓN INICIADA" in linea:
                # Intentar extraer solo la fecha
                match = re.search(r'SESIÓN INICIADA: (.*)', linea)
                if match:
                    sesiones.append(match.group(1))
                else:
                    sesiones.append(linea.strip())
        
        return sesiones


# ─────────────────────────────────────────────
# CLASE PARA VISUALIZACIÓN DEL LOG
# ─────────────────────────────────────────────

class VisorLog:
    """
    Clase que maneja la visualización formateada del log.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES.
    """
    
    def __init__(self, colores: ManejadorColores):
        """
        Constructor del visor de log.
        
        Parámetros:
            colores (ManejadorColores): Instancia del manejador de colores
        """
        self._colores = colores
    
    def mostrar_linea(self, linea: str, con_color: bool = True) -> None:
        """
        Muestra una línea del log con formato y color opcional.
        
        Parámetros:
            linea (str): Línea a mostrar
            con_color (bool): Si se deben aplicar colores
        """
        fecha, nivel, mensaje = ParseadorLog.parsear_linea(linea)
        
        if fecha is None:
            # Es una línea de separación o formato diferente
            print(linea.rstrip())
            return
        
        if con_color and nivel in Configuracion.COLORES:
            fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")
            fecha_coloreada = self._colores.cyan(fecha_str)
            nivel_coloreado = getattr(self._colores, nivel.lower(), self._colores.info)(f"[{nivel}]")
            print(f"{fecha_coloreada} {nivel_coloreado} {mensaje}")
        else:
            print(f"{fecha.strftime('%Y-%m-%d %H:%M:%S')} [{nivel}] {mensaje}")
    
    def mostrar_lista(self, lineas: List[str], titulo: str = None) -> None:
        """
        Muestra una lista de líneas del log con un título opcional.
        
        Parámetros:
            lineas (List[str]): Lista de líneas a mostrar
            titulo (str): Título opcional para la sección
        """
        if titulo:
            print("\n" + "=" * 60)
            print(f"{titulo}")
            print("=" * 60)
        
        for linea in lineas:
            self.mostrar_linea(linea)
        
        if lineas:
            print(f"\n  Total de líneas: {len(lineas)}\n")
    
    def mostrar_mensaje_error(self, mensaje: str) -> None:
        """
        Muestra un mensaje de error formateado.
        
        Parámetros:
            mensaje (str): Mensaje de error
        """
        print(f"\n  ✘ {mensaje}\n")
    
    def mostrar_mensaje_info(self, mensaje: str) -> None:
        """
        Muestra un mensaje informativo formateado.
        
        Parámetros:
            mensaje (str): Mensaje informativo
        """
        print(f"\n  ℹ️ {mensaje}\n")


# ─────────────────────────────────────────────
# CLASE PARA EL MENÚ PRINCIPAL
# ─────────────────────────────────────────────

class MenuLog:
    """
    Clase que maneja la interfaz de usuario (menú) del visor de logs.
    Principio OOP: SEPARACIÓN DE RESPONSABILIDADES.
    """
    
    def __init__(self, lector: LectorLog, estadisticas: EstadisticasLog, visor: VisorLog):
        """
        Constructor del menú.
        
        Parámetros:
            lector (LectorLog): Instancia del lector de log
            estadisticas (EstadisticasLog): Instancia de estadísticas
            visor (VisorLog): Instancia del visor
        """
        self._lector = lector
        self._estadisticas = estadisticas
        self._visor = visor
    
    def _mostrar_encabezado(self) -> None:
        """Muestra el encabezado del menú."""
        print("\n" + "=" * 60)
        print(self._visor._colores.blue("📋 VISOR DEL SISTEMA DE LOGS - SOFTWARE FJ"))
        print("=" * 60)
    
    def _mostrar_opciones(self) -> None:
        """Muestra las opciones del menú."""
        print("  [1] Ver todo el log")
        print("  [2] Ver últimas N líneas")
        print("  [3] Ver sólo errores y críticos")
        print("  [4] Ver sólo advertencias")
        print("  [5] Ver sólo información")
        print("  [6] Buscar por palabra clave")
        print("  [7] Ver por rango de fechas")
        print("  [8] Estadísticas del log")
        print("  [9] Ver sesiones (inicios del sistema)")
        print("  [0] Salir")
        print("-" * 60)
    
    def _verificar_archivo(self) -> bool:
        """Verifica si el archivo de log existe y muestra advertencia si no."""
        if not self._lector.existe():
            print(f"\n⚠️  El archivo '{self._lector.ruta}' aún no existe.")
            print("   Puedes generarlo ejecutando primero:\n")
            print("     python main.py")
            print("     python pruebas.py")
            print("\n   O simplemente continúa para ver los menús.\n")
            return False
        return True
    
    def _opcion_ver_todo(self) -> None:
        """Opción 1: Ver todo el log."""
        lineas = self._lector.leer_todas()
        if lineas:
            self._visor.mostrar_lista(lineas, "📄 LOG COMPLETO")
    
    def _opcion_ver_ultimas_n(self) -> None:
        """Opción 2: Ver últimas N líneas."""
        lineas = self._lector.leer_todas()
        if not lineas:
            return
        
        try:
            n = int(input("  ¿Cuántas líneas quieres ver? (default 20): ").strip() or "20")
        except ValueError:
            n = 20
        
        ultimas = lineas[-n:] if len(lineas) >= n else lineas
        self._visor.mostrar_lista(ultimas, f"📄 ÚLTIMAS {len(ultimas)} LÍNEAS DEL LOG")
        print(f"  Mostradas {len(ultimas)} de {len(lineas)} líneas totales.\n")
    
    def _opcion_ver_errores_criticos(self) -> None:
        """Opción 3: Ver sólo errores y críticos."""
        print("\n  Mostrando ERRORES y CRÍTICOS...")
        errores = self._estadisticas.filtrar_por_nivel("ERROR")
        criticos = self._estadisticas.filtrar_por_nivel("CRITICO")
        
        self._visor.mostrar_lista(errores, "📄 REGISTROS [ERROR]")
        self._visor.mostrar_lista(criticos, "📄 REGISTROS [CRITICO]")
    
    def _opcion_ver_advertencias(self) -> None:
        """Opción 4: Ver sólo advertencias."""
        lineas = self._estadisticas.filtrar_por_nivel("ADVERTENCIA")
        self._visor.mostrar_lista(lineas, "📄 REGISTROS [ADVERTENCIA]")
    
    def _opcion_ver_info(self) -> None:
        """Opción 5: Ver sólo información."""
        lineas = self._estadisticas.filtrar_por_nivel("INFO")
        self._visor.mostrar_lista(lineas, "📄 REGISTROS [INFO]")
    
    def _opcion_buscar_palabra(self) -> None:
        """Opción 6: Buscar por palabra clave."""
        palabra = input("  Palabra o frase a buscar: ").strip().lower()
        if not palabra:
            self._visor.mostrar_mensaje_info("No ingresaste nada que buscar.")
            return
        
        lineas = self._estadisticas.filtrar_por_palabra(palabra)
        self._visor.mostrar_lista(lineas, f"🔍 BÚSQUEDA: '{palabra}' - Total: {len(lineas)} coincidencias")
    
    def _opcion_ver_por_fecha(self) -> None:
        """Opción 7: Ver por rango de fechas."""
        fecha_inicio_str = input("  Fecha inicial (YYYY-MM-DD): ").strip()
        fecha_fin_str = input("  Fecha final (YYYY-MM-DD): ").strip()
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
        except ValueError:
            self._visor.mostrar_mensaje_error("Formato de fecha inválido. Usa YYYY-MM-DD")
            return
        
        lineas = self._estadisticas.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        self._visor.mostrar_lista(lineas, f"📅 RANGO: {fecha_inicio_str} → {fecha_fin_str} - Total: {len(lineas)} registros")
    
    def _opcion_mostrar_estadisticas(self) -> None:
        """Opción 8: Mostrar estadísticas del log."""
        total_lineas = self._estadisticas.total_lineas()
        total_dias = self._estadisticas.total_dias()
        conteo_niveles = self._estadisticas.conteo_por_nivel()
        acciones = self._estadisticas.conteo_acciones()
        
        print("\n" + "=" * 60)
        print("📊 ESTADÍSTICAS DEL SISTEMA DE LOGS")
        print("=" * 60)
        
        print(f"\n  📁 Archivo        : {self._lector.ruta}")
        print(f"  📏 Líneas totales : {total_lineas}")
        print(f"  📅 Días con logs  : {total_dias}")
        
        print(f"\n  🎚️  POR NIVEL:")
        emojis = {"INFO": "ℹ️", "ADVERTENCIA": "⚠️", "ERROR": "❌", "CRITICO": "💀"}
        for nivel in Configuracion.NIVELES_VALIDOS:
            cantidad = conteo_niveles.get(nivel, 0)
            emoji = emojis.get(nivel, "📝")
            print(f"     {emoji} {nivel:<12}: {cantidad}")
        
        print(f"\n  🏷️  ACCIONES REGISTRADAS:")
        print(f"     👤 Clientes registrados   : {acciones['registrado']}")
        print(f"     ✅ Reservas confirmadas   : {acciones['confirmada']}")
        print(f"     ❌ Reservas canceladas    : {acciones['cancelada']}")
        print(f"     🏁 Reservas procesadas    : {acciones['procesada']}")
        print(f"     🐛 Errores capturados     : {acciones['error']}")
        print(f"     ⚡ Advertencias           : {acciones['advertencia']}")
        
        print("\n" + "=" * 60 + "\n")
    
    def _opcion_ver_sesiones(self) -> None:
        """Opción 9: Ver sesiones (inicios del sistema)."""
        sesiones = self._estadisticas.obtener_sesiones()
        
        print("\n" + "=" * 60)
        print(f"🔄 SESIONES DEL SISTEMA (Total: {len(sesiones)})")
        print("=" * 60)
        
        for i, sesion in enumerate(sesiones, 1):
            print(f"  {i}. {sesion}")
        
        if not sesiones:
            print("  No hay sesiones registradas aún.")
        
        print()
    
    def ejecutar(self) -> None:
        """Ejecuta el bucle principal del menú."""
        self._verificar_archivo()
        
        while True:
            self._mostrar_encabezado()
            self._mostrar_opciones()
            
            opcion = input("  Elige una opción: ").strip()
            
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
            
            if opcion in acciones:
                acciones[opcion]()
            elif opcion == "0":
                print("\n  👋 ¡Hasta luego!\n")
                break
            else:
                print("  Opción inválida. Intenta de nuevo.\n")
    
    def ejecutar_simple(self, opcion: str) -> None:
        """
        Ejecuta una opción específica (para integración con otros sistemas).
        
        Parámetros:
            opcion (str): Opción del menú (1-9)
        """
        self._verificar_archivo()
        
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
        
        if opcion in acciones:
            acciones[opcion]()
        else:
            print(f"  Opción '{opcion}' no válida.")


# ─────────────────────────────────────────────
# CLASE PRINCIPAL DEL VISOR
# ─────────────────────────────────────────────

class VisorLogSistema:
    """
    Clase principal que orquesta todo el visor de logs.
    Principios OOP: COMPOSICIÓN (tiene un lector, estadísticas, visor y menú)
    """
    
    def __init__(self, usar_colores: bool = True):
        """
        Constructor del visor de logs.
        
        Parámetros:
            usar_colores (bool): Si se deben aplicar colores en la salida
        """
        self._colores = ManejadorColores(usar_colores)
        self._lector = LectorLog()
        self._estadisticas = EstadisticasLog(self._lector)
        self._visor = VisorLog(self._colores)
        self._menu = MenuLog(self._lector, self._estadisticas, self._visor)
    
    def iniciar(self) -> None:
        """Inicia el visor de logs con el menú interactivo."""
        self._menu.ejecutar()
    
    def ejecutar_opcion(self, opcion: str) -> None:
        """
        Ejecuta una opción específica sin menú interactivo.
        
        Parámetros:
            opcion (str): Opción del menú (1-9)
        """
        self._menu.ejecutar_simple(opcion)
    
    def mostrar_ultimas(self, n: int = 20) -> None:
        """
        Muestra las últimas N líneas del log.
        
        Parámetros:
            n (int): Número de líneas a mostrar
        """
        lineas = self._lector.leer_todas()
        if lineas:
            ultimas = lineas[-n:] if len(lineas) >= n else lineas
            self._visor.mostrar_lista(ultimas, f"📄 ÚLTIMAS {len(ultimas)} LÍNEAS")
    
    def buscar(self, palabra: str) -> None:
        """
        Busca una palabra en el log y muestra resultados.
        
        Parámetros:
            palabra (str): Palabra o frase a buscar
        """
        lineas = self._estadisticas.filtrar_por_palabra(palabra)
        self._visor.mostrar_lista(lineas, f"🔍 BÚSQUEDA: '{palabra}'")
    
    def estadisticas(self) -> Dict[str, Any]:
        """
        Retorna un diccionario con estadísticas del log.
        
        Retorna:
            Dict: Diccionario con estadísticas
        """
        return {
            "total_lineas": self._estadisticas.total_lineas(),
            "total_dias": self._estadisticas.total_dias(),
            "conteo_por_nivel": self._estadisticas.conteo_por_nivel(),
            "acciones": self._estadisticas.conteo_acciones(),
            "sesiones": self._estadisticas.obtener_sesiones()
        }


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

def main():
    """Función principal para ejecución directa."""
    visor = VisorLogSistema(usar_colores=True)
    visor.iniciar()


if __name__ == "__main__":
    main()

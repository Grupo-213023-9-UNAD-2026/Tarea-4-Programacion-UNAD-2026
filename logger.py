"""
logger.py
Autor: Jesús David Rodríguez Alvarado
Curso: Programación 213023 - UNAD
=========
Implementa un sistema de registro simple para el proyecto.
Escribe en `sistema.log` y además puede mostrar mensajes en consola.
"""

# Importamos builtins para conservar una referencia al print original.
import builtins
# Importamos datetime para sellar cada evento con fecha y hora.
from datetime import datetime
# Importamos os para construir la ruta del archivo de log.
import os
# Importamos sys para detectar la codificación de la consola actual.
import sys


# Guardamos la función print original para evitar recursión infinita.
_PRINT_ORIGINAL = builtins.print


# Esta función convierte un texto a una versión segura para la consola.
def _normalizar_para_consola(texto: str, destino) -> str:
    # Detectamos la codificación declarada por la salida actual.
    encoding = getattr(destino, "encoding", None) or "utf-8"
    # Reconvertimos el texto reemplazando símbolos no compatibles.
    return texto.encode(encoding, errors="replace").decode(encoding, errors="replace")


# Esta función reemplaza a print para no romper la ejecución por Unicode.
def _imprimir_seguro(*args, **kwargs) -> None:
    # Detectamos si el destino es stdout, stderr u otro flujo.
    destino = kwargs.get("file", sys.stdout)
    try:
        # Probamos imprimir normalmente antes de aplicar cualquier corrección.
        _PRINT_ORIGINAL(*args, **kwargs)
    except UnicodeEncodeError:
        # Si el destino no es la consola estándar, reenviamos el error real.
        if destino not in (sys.stdout, sys.stderr):
            raise
        # Recuperamos el separador entre argumentos o usamos el estándar.
        separador = kwargs.get("sep", " ")
        # Recuperamos el final de línea o usamos el estándar.
        fin = kwargs.get("end", "\n")
        # Recuperamos el flag de vaciado inmediato de buffer.
        vaciar = kwargs.get("flush", False)
        # Unimos todos los argumentos como el print normal.
        texto = separador.join(str(arg) for arg in args)
        # Convertimos el texto a una versión segura para la consola.
        texto_seguro = _normalizar_para_consola(texto, destino)
        # Imprimimos el texto convertido con los mismos parámetros básicos.
        _PRINT_ORIGINAL(texto_seguro, end=fin, file=destino, flush=vaciar)


# Esta función instala el print seguro para todo el proyecto.
def instalar_print_seguro() -> None:
    # Solo reemplazamos print si todavía no se había hecho antes.
    if builtins.print is not _imprimir_seguro:
        builtins.print = _imprimir_seguro


# Instalamos la protección apenas se importa el módulo.
instalar_print_seguro()


# Esta clase centraliza la configuración estática del logger.
class ConfiguracionLogger:
    """Constantes y rutas usadas por el sistema de logs."""

    # Construimos la ruta del log dentro de la misma carpeta del proyecto.
    ARCHIVO_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema.log")
    # Definimos el nivel informativo para eventos normales.
    NIVEL_INFO = "INFO"
    # Definimos el nivel de advertencia para situaciones no críticas.
    NIVEL_ADVERTENCIA = "ADVERTENCIA"
    # Definimos el nivel de error para fallos controlados.
    NIVEL_ERROR = "ERROR"
    # Definimos el nivel crítico para fallos graves.
    NIVEL_CRITICO = "CRITICO"
    # Reunimos los niveles válidos en una sola colección.
    NIVELES_VALIDOS = [
        NIVEL_INFO,
        NIVEL_ADVERTENCIA,
        NIVEL_ERROR,
        NIVEL_CRITICO,
    ]
    # Definimos una línea separadora ASCII compatible con casi cualquier consola.
    SEPARADOR_SESION = "=" * 60
    # Definimos el texto fijo que identifica el inicio de sesión del sistema.
    TEXTO_SESION = "SISTEMA SOFTWARE FJ - SESION INICIADA"
    # Definimos prefijos legibles y completamente ASCII para la consola.
    ETIQUETAS_CONSOLA = {
        NIVEL_INFO: "[OK]",
        NIVEL_ADVERTENCIA: "[WARN]",
        NIVEL_ERROR: "[ERROR]",
        NIVEL_CRITICO: "[CRIT]",
    }


# Esta clase transforma eventos del logger en líneas de texto.
class FormateadorLog:
    """Se encarga de dar formato uniforme a cada registro."""

    @staticmethod
    def formatear_linea(nivel: str, mensaje: str, fecha: datetime | None = None) -> str:
        # Si no llega una fecha externa, usamos el momento actual.
        fecha_evento = fecha or datetime.now()
        # Formateamos la fecha en un formato legible y estable.
        fecha_formateada = fecha_evento.strftime("%Y-%m-%d %H:%M:%S")
        # Devolvemos la línea lista para escribir en el archivo.
        return f"[{fecha_formateada}] [{nivel}] {mensaje}\n"

    @staticmethod
    def formatear_separador_sesion() -> str:
        # Tomamos la fecha actual para marcar el inicio de la ejecución.
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Construimos un bloque visual simple y compatible con consola.
        return (
            f"\n{ConfiguracionLogger.SEPARADOR_SESION}\n"
            f"  {ConfiguracionLogger.TEXTO_SESION}: {marca}\n"
            f"{ConfiguracionLogger.SEPARADOR_SESION}\n"
        )


# Esta clase encapsula la lectura y escritura del archivo de log.
class EscritorLog:
    """Maneja la persistencia del log en disco."""

    def __init__(self, ruta_archivo: str | None = None):
        # Usamos la ruta personalizada o la ruta por defecto del proyecto.
        self._ruta = ruta_archivo or ConfiguracionLogger.ARCHIVO_LOG

    @property
    def ruta(self) -> str:
        # Exponemos la ruta del archivo para otros componentes.
        return self._ruta

    def escribir(self, contenido: str) -> bool:
        try:
            # Abrimos el archivo en modo agregar para no borrar historial previo.
            with open(self._ruta, "a", encoding="utf-8") as archivo:
                # Escribimos el bloque de texto recibido.
                archivo.write(contenido)
            # Indicamos éxito a quien llamó.
            return True
        except OSError as error:
            # Informamos el problema sin detener el resto del sistema.
            print(f"[LOGGER] No se pudo escribir en {self._ruta}: {error}")
            # Indicamos que la operación falló.
            return False

    def leer_ultimas_lineas(self, cantidad: int = 20) -> list[str] | None:
        try:
            # Si el archivo no existe aún, no hay nada para devolver.
            if not os.path.exists(self._ruta):
                return None
            # Abrimos el archivo en modo lectura con codificación UTF-8.
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                # Cargamos todas las líneas para extraer el tramo final.
                lineas = archivo.readlines()
            # Devolvemos las últimas líneas solicitadas o todas si son menos.
            return lineas[-cantidad:] if len(lineas) >= cantidad else lineas
        except OSError as error:
            # Informamos el problema sin propagar una excepción técnica.
            print(f"[LOGGER] No se pudo leer el archivo de log: {error}")
            # Devolvemos None para indicar que hubo fallo de lectura.
            return None


# Esta clase ofrece la interfaz principal de registro del proyecto.
class Logger:
    """Logger del sistema con salida a archivo y consola."""

    def __init__(self, ruta_archivo: str | None = None):
        # Creamos el formateador que preparará cada línea de log.
        self._formateador = FormateadorLog()
        # Creamos el escritor responsable de la persistencia en disco.
        self._escritor = EscritorLog(ruta_archivo)

    def _registrar(self, nivel: str, mensaje: str, mostrar_consola: bool = True) -> None:
        # Formateamos la línea antes de enviarla al archivo.
        linea = self._formateador.formatear_linea(nivel, mensaje)
        # Intentamos persistir el evento en el archivo de log.
        self._escritor.escribir(linea)
        # Si se pidió salida visible, también mostramos el evento en consola.
        if mostrar_consola:
            self._mostrar_en_consola(nivel, mensaje)

    def _mostrar_en_consola(self, nivel: str, mensaje: str) -> None:
        # Buscamos una etiqueta ASCII según el nivel del evento.
        etiqueta = ConfiguracionLogger.ETIQUETAS_CONSOLA.get(nivel, "[LOG]")
        # Imprimimos el mensaje con un formato uniforme y sin redundancia visual.
        print(f"  {etiqueta} {mensaje}")

    def info(self, mensaje: str) -> None:
        # Registramos un evento informativo.
        self._registrar(ConfiguracionLogger.NIVEL_INFO, mensaje)

    def advertencia(self, mensaje: str) -> None:
        # Registramos un evento de advertencia.
        self._registrar(ConfiguracionLogger.NIVEL_ADVERTENCIA, mensaje)

    def error(self, mensaje: str) -> None:
        # Registramos un evento de error controlado.
        self._registrar(ConfiguracionLogger.NIVEL_ERROR, mensaje)

    def critico(self, mensaje: str) -> None:
        # Registramos un evento crítico.
        self._registrar(ConfiguracionLogger.NIVEL_CRITICO, mensaje)

    def iniciar_sesion(self) -> None:
        # Preparamos el bloque que separa visualmente la ejecución actual.
        separador = self._formateador.formatear_separador_sesion()
        # Escribimos el separador en el archivo para marcar una nueva sesión.
        self._escritor.escribir(separador)
        # Mostramos el mismo separador en la consola para el usuario.
        print(separador, end="")

    def mostrar_log(self, ultimas_n_lineas: int = 20) -> None:
        # Leemos las últimas líneas solicitadas del archivo.
        lineas = self._escritor.leer_ultimas_lineas(ultimas_n_lineas)
        # Si no hay archivo o lectura disponible, lo informamos al usuario.
        if lineas is None:
            print("El archivo de log aun no existe.")
            return
        # Mostramos un encabezado simple para contextualizar el bloque.
        print(f"\n--- Ultimas {len(lineas)} lineas del log ---")
        # Imprimimos cada línea respetando el salto que ya trae el archivo.
        for linea in lineas:
            print(linea, end="")
        # Cerramos el bloque con un pie de sección.
        print("--- Fin del log ---\n")

    def limpiar_log(self) -> bool:
        try:
            # Abrimos el archivo en modo escritura para vaciarlo por completo.
            with open(self._escritor.ruta, "w", encoding="utf-8") as archivo:
                # Escribimos una cadena vacía para dejar el archivo limpio.
                archivo.write("")
            # Indicamos éxito a quien llamó.
            return True
        except OSError as error:
            # Informamos el problema de limpieza sin cerrar la aplicación.
            print(f"[LOGGER] No se pudo limpiar el archivo de log: {error}")
            # Indicamos que la operación falló.
            return False


# Esta variable almacenará la única instancia compartida del logger.
_logger_instancia: Logger | None = None


# Esta función entrega la instancia singleton del logger del proyecto.
def obtener_logger() -> Logger:
    # Declaramos que vamos a reutilizar la variable global del módulo.
    global _logger_instancia
    # Si aún no existe una instancia, la creamos.
    if _logger_instancia is None:
        _logger_instancia = Logger()
    # Devolvemos la misma instancia para todos los módulos.
    return _logger_instancia


# Esta función mantiene compatibilidad con código que llama `registrar`.
def registrar(nivel: str, mensaje: str) -> None:
    # Recuperamos la instancia compartida del logger.
    logger = obtener_logger()
    # Derivamos el método correcto según el nivel solicitado.
    if nivel == ConfiguracionLogger.NIVEL_INFO:
        logger.info(mensaje)
    elif nivel == ConfiguracionLogger.NIVEL_ADVERTENCIA:
        logger.advertencia(mensaje)
    elif nivel == ConfiguracionLogger.NIVEL_ERROR:
        logger.error(mensaje)
    elif nivel == ConfiguracionLogger.NIVEL_CRITICO:
        logger.critico(mensaje)
    else:
        # Si el nivel no es reconocido, usamos INFO como valor por defecto.
        logger.info(mensaje)


# Esta función expone el registro informativo en formato simple.
def info(mensaje: str) -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().info(mensaje)


# Esta función expone el registro de advertencia en formato simple.
def advertencia(mensaje: str) -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().advertencia(mensaje)


# Esta función expone el registro de error en formato simple.
def error(mensaje: str) -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().error(mensaje)


# Esta función expone el registro crítico en formato simple.
def critico(mensaje: str) -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().critico(mensaje)


# Esta función expone el marcador de inicio de sesión.
def iniciar_sesion() -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().iniciar_sesion()


# Esta función expone la visualización rápida del log reciente.
def mostrar_log(ultimas_n_lineas: int = 20) -> None:
    # Delegamos la operación al logger singleton.
    obtener_logger().mostrar_log(ultimas_n_lineas)


# Este bloque solo se ejecuta si el archivo se corre directamente.
if __name__ == "__main__":
    # Informamos que comenzarán las pruebas manuales del logger.
    print("Probando el sistema de logs...")
    # Creamos una instancia local solo para esta prueba autónoma.
    logger_prueba = Logger()
    # Marcamos el inicio de sesión de la prueba.
    logger_prueba.iniciar_sesion()
    # Registramos un ejemplo de mensaje informativo.
    logger_prueba.info("Mensaje de prueba INFO")
    # Registramos un ejemplo de advertencia.
    logger_prueba.advertencia("Mensaje de prueba ADVERTENCIA")
    # Registramos un ejemplo de error.
    logger_prueba.error("Mensaje de prueba ERROR")
    # Registramos un ejemplo de evento crítico.
    logger_prueba.critico("Mensaje de prueba CRITICO")
    # Mostramos parte del log recién generado.
    logger_prueba.mostrar_log(10)
    # Indicamos al usuario dónde quedó guardado el archivo de prueba.
    print(f"\nLas pruebas se han guardado en: {logger_prueba._escritor.ruta}")
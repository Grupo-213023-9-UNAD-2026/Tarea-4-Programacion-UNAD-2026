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
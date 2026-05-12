# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

> Proyecto academico - Curso Programacion (213023) - Ingenieria de Sistemas - UNAD  
> Fase 4 - Programacion Orientada a Objetos con manejo avanzado de excepciones

---

## Descripcion

Software FJ es una aplicacion de consola desarrollada en Python para gestionar clientes, servicios y reservas sin usar base de datos.  
Toda la informacion se mantiene en memoria por medio de objetos y listas, y los eventos importantes del sistema se registran en el archivo `sistema.log`.

El proyecto fue construido con enfoque de Programacion Orientada a Objetos, usando clases, encapsulacion, herencia, abstraccion, polimorfismo y manejo de excepciones personalizadas.

---

## Objetivo del sistema

Permitir la administracion basica de una empresa ficticia que ofrece servicios como:

- Registro y consulta de clientes.
- Registro y administracion de servicios.
- Creacion, confirmacion, cancelacion y procesamiento de reservas.
- Generacion de reportes basicos.
- Registro de eventos y errores en un archivo de log.
- Visualizacion del historial del sistema desde un visor independiente.

---

## Integrantes y roles

| # | Nombre | Responsabilidad principal |
|---|--------|---------------------------|
| 1 | Paula | `cliente.py`, `excepciones.py` - Clases de clientes y errores del sistema |
| 2 | Jesus | `reserva.py`, `logger.py`, `pruebas.py` - Reservas, logs y simulacion |
| 3 | Yirleira | Apoyo en integracion, revision de `main.py` y `README.md` |
| 4 | Valery | `servicio.py` - Servicios, documentacion de clases y pruebas adicionales |
| 5 | Ezequiel | `main.py`, `README.md`, `ver_log.py` - Menu principal, documentacion y visor del log |

---

## Caracteristicas principales

- Interfaz de consola organizada por menus.
- Gestion de clientes con validaciones de nombre, email y estado.
- Catalogo de servicios con tres tipos principales:
  `SalaReuniones`, `AlquilerEquipo` y `AsesoriaTecnica`.
- Reservas con estados `PENDIENTE`, `CONFIRMADA`, `CANCELADA` y `PROCESADA`.
- Excepciones personalizadas para controlar errores del sistema.
- Sistema de logs con niveles `INFO`, `ADVERTENCIA`, `ERROR` y `CRITICO`.
- Simulacion automatica de pruebas desde `pruebas.py`.
- Visor independiente del log desde `ver_log.py`.

---

## Estructura del repositorio

```text
Codigo Comentado/
|-- cliente.py
|-- excepciones.py
|-- logger.py
|-- main.py
|-- pruebas.py
|-- README.md
|-- reserva.py
|-- servicio.py
|-- sistema.log
|-- ver_log.py
`-- __pycache__/
```

### Descripcion de archivos

- `main.py`
  Punto de entrada principal del sistema. Crea los gestores, las vistas y ejecuta el menu general de clientes, servicios, reservas, reportes y simulacion.

- `cliente.py`
  Define la clase abstracta `Entidad`, la clase `Cliente` y el `GestorClientes`. Contiene validaciones de nombre, correo, activacion y desactivacion de clientes.

- `servicio.py`
  Define la clase abstracta `Servicio` y sus tres especializaciones:
  `SalaReuniones`, `AlquilerEquipo` y `AsesoriaTecnica`. Tambien incluye el `GestorServicios`.

- `reserva.py`
  Define la clase `Reserva`, los estados de la reserva y el `GestorReservas`. Maneja el ciclo de vida de cada reserva y su costo.

- `excepciones.py`
  Contiene todas las excepciones personalizadas del sistema agrupadas por clientes, servicios, reservas y calculos.

- `logger.py`
  Implementa el sistema de registro de eventos del proyecto. Guarda informacion en `sistema.log` y ofrece funciones de compatibilidad para los demas modulos.

- `pruebas.py`
  Ejecuta una simulacion automatica con pruebas funcionales del sistema para clientes, servicios y reservas.

- `ver_log.py`
  Permite visualizar el archivo `sistema.log`, filtrar por nivel, buscar palabras, consultar por fechas, ver sesiones y mostrar estadisticas.

- `sistema.log`
  Archivo generado por el sistema para registrar eventos, advertencias y errores.

- `README.md`
  Documento de presentacion, estructura y guia general del proyecto.

---

## Estructura POO del proyecto

El sistema conserva una organizacion orientada a objetos:

- **Abstraccion**
  Se usan clases abstractas como `Entidad` y `Servicio` para definir contratos comunes.

- **Encapsulacion**
  Los atributos se manejan como privados o protegidos, y el acceso se realiza mediante propiedades y metodos.

- **Herencia**
  `Cliente` hereda de `Entidad`, y los distintos servicios heredan de `Servicio`.

- **Polimorfismo**
  Cada tipo de servicio implementa su propia forma de calcular costos y describirse.

- **Composicion**
  Una `Reserva` se construye usando un `Cliente` y un `Servicio`.

---

## Requisitos

- Python 3.10 o superior.
- No requiere librerias externas.

---

## Ejecucion del proyecto

### 1. Ejecutar el sistema principal

```bash
python main.py
```

### 2. Ejecutar la simulacion automatica

```bash
python pruebas.py
```

### 3. Visualizar el archivo de logs

```bash
python ver_log.py
```

---

## Flujo general del sistema

1. Se registran clientes.
2. Se agregan servicios al catalogo.
3. Se crean reservas asociando un cliente con un servicio.
4. La reserva puede confirmarse, cancelarse o procesarse.
5. Cada evento importante queda registrado en `sistema.log`.
6. El historial puede revisarse desde `ver_log.py`.

---

## Manejo de errores

El proyecto usa excepciones personalizadas para mantener controlados los errores y evitar que el programa falle de forma abrupta.

Algunos grupos de excepciones son:

- `ErrorCliente`
- `ErrorServicio`
- `ErrorReserva`
- `ErrorCalculoCosto`
- `ErrorSistema`

Esto permite mostrar mensajes claros al usuario y registrar el detalle en el log.

---

## Estado actual del proyecto

El codigo se encuentra organizado por modulos, mantiene la estructura POO y cuenta con:

- Menu principal funcional.
- Simulacion automatica funcional.
- Sistema de logs funcional.
- Visor de logs funcional.
- Validaciones y manejo de errores integrados.

---

## Observacion

El archivo `sistema.log` se genera y actualiza automaticamente cuando se ejecutan `main.py`, `pruebas.py` o los modulos que escriben eventos en el sistema de logs.

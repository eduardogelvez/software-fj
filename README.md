# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la Fase 4 (Prácticas simuladas) del curso **Programación (213023)** – UNAD, Ingeniería de Sistemas.

Sistema orientado a objetos en Python, **sin base de datos**, que gestiona clientes, servicios (reserva de salas, alquiler de equipos y asesorías especializadas) y reservas para la empresa Software FJ. Toda la información vive en objetos y listas en memoria; el único archivo que se escribe es el log de eventos y errores.

## Cómo ejecutarlo

Requiere Python 3.8 o superior. No necesita librerías externas.

```bash
python main.py
```

Al terminar, el detalle de eventos y errores queda en `logs/software_fj.log`.

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y sus hijas, con códigos FJ-xxx). |
| `utilidades.py` | Configuración del archivo de logs, registro de errores encadenados y formato de pesos. |
| `entidades.py` | Clase abstracta `EntidadBase` y clase `Cliente` con validaciones y datos encapsulados. |
| `servicios.py` | Clase abstracta `Servicio` y sus tres hijas: `ReservaSala`, `AlquilerEquipo` y `Asesoria`. |
| `reserva.py` | Clase `Reserva` con estados (pendiente, confirmada, cancelada, procesada). |
| `sistema.py` | Clase `SistemaSoftwareFJ`: listas internas y operaciones protegidas con manejo de excepciones. |
| `main.py` | Simulación de 32 operaciones válidas e inválidas. |

## Cómo se cumple cada requisito

| Requisito | Dónde está |
|---|---|
| Clase abstracta general | `EntidadBase` (`entidades.py`), con `describir()` y `validar()` abstractos. |
| Cliente con validaciones y encapsulación | `Cliente`: atributos privados (`__documento`, `__correo`...), propiedades con setters que validan, documento enmascarado. |
| Servicio abstracto + 3 servicios | `Servicio` → `ReservaSala`, `AlquilerEquipo`, `Asesoria`; cada una sobrescribe `costo_base()`, `validar_parametros()` y `describir()`. |
| Polimorfismo | `calcular_costo()` y `resumen()` llaman los métodos sobrescritos sin saber qué tipo de servicio es. |
| Reserva con confirmación, cancelación y procesamiento | `Reserva.confirmar()`, `cancelar()`, `procesar()`. |
| Métodos sobrecargados | `calcular_costo(d)`, `calcular_costo(d, impuesto)`, `calcular_costo(d, impuesto, descuento)` y `cotizar()` con `@singledispatchmethod` (variantes para `int/float`, `dict` y tipo no soportado). |
| Excepciones personalizadas | `excepciones.py` (10 clases). |
| `try/except` | En todas las operaciones de `sistema.py` y en `main.ejecutar_operacion()`. |
| `try/except/else` | `registrar_cliente`, `agregar_servicio`, `crear_reserva`, `Reserva.confirmar`, entre otros. |
| `try/except/finally` | `Reserva.procesar()` y `SistemaSoftwareFJ.procesar_reserva()` (este último con los cuatro bloques). |
| Encadenamiento (`raise ... from`) | Creación de reservas, confirmación con servicio no disponible, cobro con descuento inválido, servicio con datos incompletos. |
| Archivo de logs | `logs/software_fj.log` (eventos INFO/WARNING, errores ERROR con su cadena de causas, CRITICAL con traza completa). |
| Mínimo 10 operaciones | `main.py` ejecuta 32 operaciones y el programa nunca se detiene. |

## Integrantes

- Jose Eduardo Gelvez Peñaranda

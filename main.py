"""
main.py
-------
Punto de entrada del sistema Software FJ.
Simula operaciones completas (válidas e inválidas) para demostrar que
el programa sigue funcionando aunque se presenten errores.

Ejecutar con:  python main.py
"""

from sistema import SistemaSoftwareFJ  # Clase central del sistema
from utilidades import obtener_logger, ARCHIVO_LOG  # Logger y ruta del archivo de logs


def ejecutar_operacion(numero, descripcion, accion):  # Ejecuta una operación con una red de seguridad final
    """Si ocurre un error inesperado (no previsto por el sistema), se registra y el programa continúa."""
    print(f"\n[{numero:02d}] {descripcion}")  # Muestra el número y la descripción de la operación
    try:  # Bloque de seguridad
        return accion()  # Ejecuta la operación (una función lambda)
    except Exception as error:  # Atrapa CUALQUIER error que se haya escapado (por ejemplo un TypeError de Python)
        obtener_logger().critical(f"Operación {numero} - error inesperado: {error!r}", exc_info=True)  # Log con traza completa
        print(f"   ✗ Error inesperado controlado: {type(error).__name__}: {error}")  # Aviso en consola
        return None  # El programa sigue con la siguiente operación


def main():  # Función principal
    sistema = SistemaSoftwareFJ()  # Crea el sistema vacío (todo vive en memoria, sin base de datos)

    operaciones = [  # Lista de operaciones: (descripción, función a ejecutar)
        # ---------------- CLIENTES ----------------
        ("Registrar cliente válido (Laura Martínez)",
         lambda: sistema.registrar_cliente("1090456789", "laura martínez", "Laura.Martinez@gmail.com", "3104567890")),
        ("Registrar cliente válido (Carlos Peña)",
         lambda: sistema.registrar_cliente("88234567", "Carlos Peña", "carlos.pena@empresa.co", "3157894561")),
        ("Registrar cliente con correo inválido",
         lambda: sistema.registrar_cliente("1093111222", "Andrés Ruiz", "andres.ruiz@", "3001234567")),
        ("Registrar cliente sin nombre (parámetro faltante)",
         lambda: sistema.registrar_cliente("1094555666", "", "sin.nombre@correo.com", "3201112233")),
        ("Registrar cliente con teléfono fijo (no es celular)",
         lambda: sistema.registrar_cliente("1095777888", "Marta Gómez", "marta@correo.com", "5771234")),
        ("Registrar cliente duplicado (mismo documento de Laura)",
         lambda: sistema.registrar_cliente("1090456789", "Laura Copia", "otra@correo.com", "3109998877")),

        # ---------------- SERVICIOS ----------------
        ("Crear servicio válido: sala de juntas",
         lambda: sistema.agregar_servicio("sala", nombre="Sala de juntas Norte", tarifa_hora=80000, capacidad=12)),
        ("Crear servicio válido: alquiler de portátiles",
         lambda: sistema.agregar_servicio("equipo", nombre="Portátiles Lenovo", tarifa_dia=45000,
                                          tipo_equipo="Portátil", unidades=5)),
        ("Crear servicio válido: asesoría en ciberseguridad",
         lambda: sistema.agregar_servicio("asesoria", nombre="Asesoría en ciberseguridad", tarifa_hora=150000,
                                          especialidad="Ciberseguridad", nivel="experto")),
        ("Crear sala con tarifa negativa",
         lambda: sistema.agregar_servicio("sala", nombre="Sala Sur", tarifa_hora=-5000, capacidad=6)),
        ("Crear servicio de un tipo que no existe",
         lambda: sistema.agregar_servicio("catering", nombre="Refrigerios", tarifa=20000)),
        ("Crear asesoría sin especialidad (datos incompletos)",
         lambda: sistema.agregar_servicio("asesoria", nombre="Asesoría contable", tarifa_hora=90000)),
        ("Crear asesoría con nivel inexistente",
         lambda: sistema.agregar_servicio("asesoria", nombre="Asesoría en redes", tarifa_hora=120000,
                                          especialidad="Redes", nivel="master")),

        # ---------------- COTIZACIONES (método sobrecargado) ----------------
        ("Cotizar asesoría pasando solo un número (2 horas)",
         lambda: sistema.cotizar_servicio("ASE-001", 2)),
        ("Cotizar sala pasando un diccionario con descuento",
         lambda: sistema.cotizar_servicio("SAL-001", {"duracion": 8, "asistentes": 10, "descuento": 0.05})),
        ("Cotizar pasando un texto (tipo no soportado)",
         lambda: sistema.cotizar_servicio("SAL-001", "cuatro horas")),

        # ---------------- RESERVAS ----------------
        ("Crear reserva válida: Laura reserva la sala 4 horas para 8 personas",
         lambda: sistema.crear_reserva("1090456789", "SAL-001", 4, asistentes=8)),
        ("Confirmar la reserva RES-001",
         lambda: sistema.confirmar_reserva("RES-001")),
        ("Procesar el cobro de RES-001 con IVA y 10 % de descuento",
         lambda: sistema.procesar_reserva("RES-001", impuesto=0.19, descuento=0.10)),
        ("Crear reserva con más asistentes que la capacidad de la sala",
         lambda: sistema.crear_reserva("88234567", "SAL-001", 3, asistentes=30)),
        ("Crear reserva para un cliente que no existe",
         lambda: sistema.crear_reserva("123456", "EQU-001", 2, cantidad=1)),
        ("Crear reserva válida: Carlos alquila 2 portátiles por 3 días",
         lambda: sistema.crear_reserva("88234567", "EQU-001", 3, cantidad=2)),
        ("Poner los portátiles en mantenimiento (deshabilitar EQU-001)",
         lambda: sistema.cambiar_disponibilidad("EQU-001", False)),
        ("Confirmar RES-002 con el servicio deshabilitado",
         lambda: sistema.confirmar_reserva("RES-002")),
        ("Crear nueva reserva sobre un servicio no disponible",
         lambda: sistema.crear_reserva("1090456789", "EQU-001", 1)),
        ("Habilitar de nuevo EQU-001 y confirmar RES-002",
         lambda: sistema.cambiar_disponibilidad("EQU-001", True) and sistema.confirmar_reserva("RES-002")),
        ("Procesar RES-002 con un descuento imposible (150 %)",
         lambda: sistema.procesar_reserva("RES-002", descuento=1.5)),
        ("Cancelar RES-002 indicando el motivo",
         lambda: sistema.cancelar_reserva("RES-002", "El cliente aplazó el evento")),
        ("Intentar cancelar RES-001, que ya fue cobrada",
         lambda: sistema.cancelar_reserva("RES-001", "Error del cliente")),
        ("Crear reserva de asesoría presencial de 2 horas para Laura",
         lambda: sistema.crear_reserva("1090456789", "ASE-001", 2, modalidad="presencial")),
        ("Procesar RES-003 sin haberla confirmado",
         lambda: sistema.procesar_reserva("RES-003")),
        ("Llamar una operación con argumentos faltantes (error inesperado de Python)",
         lambda: sistema.crear_reserva("1090456789")),
    ]

    for numero, (descripcion, accion) in enumerate(operaciones, start=1):  # Recorre y numera las operaciones
        ejecutar_operacion(numero, descripcion, accion)  # Ejecuta cada una con su red de seguridad

    sistema.resumen()  # Al final muestra el resumen de todo lo que quedó en memoria
    print(f"\nEl detalle de eventos y errores quedó en: {ARCHIVO_LOG}")  # Indica dónde está el log


if __name__ == "__main__":  # Solo se ejecuta si se corre este archivo directamente
    main()  # Llama a la función principal

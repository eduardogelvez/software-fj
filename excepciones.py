"""
excepciones.py
--------------
Excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, así el sistema puede atrapar cualquier
error "propio" con un solo except y diferenciarlo de errores inesperados
de Python (TypeError, KeyError, etc.).
"""


class SoftwareFJError(Exception):  # Excepción base del sistema; hereda de Exception de Python
    """Error general del sistema Software FJ."""

    codigo = "FJ-000"  # Código por defecto; cada subclase define el suyo para identificarla en el log

    def __init__(self, mensaje):  # Recibe el mensaje que explica qué salió mal
        super().__init__(mensaje)  # Le pasa el mensaje al constructor de Exception
        self.mensaje = mensaje  # Guarda el mensaje como atributo para poder consultarlo después

    def __str__(self):  # Define cómo se ve el error cuando se imprime o se escribe en el log
        return f"[{self.codigo}] {self.mensaje}"  # Ejemplo: [FJ-110] El correo no es válido


# ---------------------------------------------------------------------
# Errores de validación de datos
# ---------------------------------------------------------------------
class ValidacionError(SoftwareFJError):  # Agrupa todos los errores causados por datos incorrectos
    """Los datos recibidos no cumplen las reglas del sistema."""
    codigo = "FJ-100"  # Código del grupo de validaciones


class ParametroFaltanteError(ValidacionError):  # Se lanza cuando un dato obligatorio llega vacío o no llega
    """Falta un dato obligatorio."""
    codigo = "FJ-101"  # Código para parámetros faltantes


class DatoInvalidoError(ValidacionError):  # Se lanza cuando un dato llega pero con tipo o valor incorrecto
    """Un dato tiene un tipo o un valor fuera de rango."""
    codigo = "FJ-102"  # Código para datos inválidos


class ClienteInvalidoError(ValidacionError):  # Errores específicos de los datos de un cliente
    """Los datos del cliente no son válidos."""
    codigo = "FJ-110"  # Código para clientes inválidos


class ServicioInvalidoError(ValidacionError):  # Errores específicos al crear o configurar un servicio
    """Los datos del servicio no son válidos."""
    codigo = "FJ-120"  # Código para servicios inválidos


# ---------------------------------------------------------------------
# Errores de operación del negocio
# ---------------------------------------------------------------------
class ServicioNoDisponibleError(SoftwareFJError):  # El servicio existe pero no se puede usar (mantenimiento, etc.)
    """El servicio solicitado no está disponible."""
    codigo = "FJ-200"  # Código para servicios no disponibles


class ReservaError(SoftwareFJError):  # Errores al crear, confirmar o procesar una reserva
    """No se pudo completar una operación sobre una reserva."""
    codigo = "FJ-300"  # Código general de reservas


class OperacionNoPermitidaError(ReservaError):  # La operación no aplica al estado actual de la reserva
    """La operación no está permitida en el estado actual."""
    codigo = "FJ-310"  # Código para operaciones no permitidas


class CalculoInconsistenteError(SoftwareFJError):  # El cálculo del costo dio un resultado ilógico o no se pudo hacer
    """El cálculo de costos dio un resultado inválido."""
    codigo = "FJ-400"  # Código para errores de cálculo


class EntidadNoEncontradaError(SoftwareFJError):  # Se buscó un cliente, servicio o reserva que no existe
    """No se encontró el cliente, servicio o reserva buscado."""
    codigo = "FJ-500"  # Código para búsquedas sin resultado

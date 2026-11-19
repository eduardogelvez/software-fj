"""
reserva.py
----------
Clase Reserva: une un cliente, un servicio, una duración y un estado.
Maneja confirmación, cancelación y procesamiento con excepciones.
"""

from datetime import datetime  # Para registrar la hora de cada cambio en el historial
from enum import Enum  # Para definir los estados posibles de una reserva de forma ordenada

from entidades import EntidadBase, Cliente  # Clase abstracta padre y clase Cliente
from servicios import Servicio  # Clase abstracta de servicios
from utilidades import formato_pesos  # Para mostrar el total en pesos colombianos
from excepciones import (  # Excepciones que usa la reserva
    ReservaError,  # Error general de reservas
    OperacionNoPermitidaError,  # Operación que no aplica al estado actual
    ParametroFaltanteError,  # Dato obligatorio faltante
    ValidacionError,  # Cualquier error de validación (para encadenarlo)
    ServicioNoDisponibleError,  # Servicio deshabilitado
    CalculoInconsistenteError,  # Error al calcular el costo
)


class EstadoReserva(Enum):  # Enumeración con los únicos estados válidos
    PENDIENTE = "Pendiente"  # Recién creada, sin confirmar
    CONFIRMADA = "Confirmada"  # Confirmada, lista para cobrar
    CANCELADA = "Cancelada"  # Cancelada por el cliente o la empresa
    PROCESADA = "Procesada"  # Cobrada y cerrada


class Reserva(EntidadBase):  # Reserva hereda de EntidadBase
    """Reserva de un servicio hecha por un cliente."""

    def __init__(self, cliente, servicio, duracion, **detalles):  # detalles: asistentes, cantidad, modalidad, etc.
        if not isinstance(cliente, Cliente):  # El cliente debe ser un objeto Cliente
            raise ReservaError("La reserva necesita un cliente válido.")  # Error si llega otra cosa
        if not isinstance(servicio, Servicio):  # El servicio debe ser un objeto Servicio (sala, equipo o asesoría)
            raise ReservaError("La reserva necesita un servicio válido.")  # Error si llega otra cosa
        try:  # Se intenta validar la solicitud con las reglas del servicio
            servicio.validar_parametros(duracion, **detalles)  # Polimorfismo: cada servicio valida a su manera
        except ValidacionError as error:  # Si la validación falla...
            raise ReservaError(  # ...se lanza un error de reserva...
                f"No se pudo crear la reserva de '{servicio.nombre}' para {cliente.nombre}."
            ) from error  # ...encadenado con la causa original
        self._cliente = cliente  # Guarda el cliente
        self._servicio = servicio  # Guarda el servicio
        self._duracion = duracion  # Guarda la duración (horas o días según el servicio)
        self._detalles = dict(detalles)  # Copia los detalles para que no cambien desde afuera
        self._estado = EstadoReserva.PENDIENTE  # Toda reserva empieza pendiente
        self._costo_total = None  # Todavía no se ha cobrado
        self._historial = []  # Lista interna con los cambios de la reserva
        super().__init__("RES")  # Asigna el id RES-00X solo si todo es válido
        self._registrar_historial("Reserva creada")  # Primer registro del historial

    # ---------------- propiedades ----------------
    @property
    def cliente(self):  # Cliente de la reserva (solo lectura)
        return self._cliente  # Devuelve el objeto Cliente

    @property
    def servicio(self):  # Servicio reservado (solo lectura)
        return self._servicio  # Devuelve el objeto Servicio

    @property
    def estado(self):  # Estado actual (solo lectura; se cambia con los métodos)
        return self._estado  # Devuelve el EstadoReserva

    @property
    def costo_total(self):  # Total cobrado; es None mientras no se procese
        return self._costo_total  # Devuelve el total

    @property
    def historial(self):  # Copia del historial para que no se modifique desde afuera
        return list(self._historial)  # Devuelve una lista nueva

    def _registrar_historial(self, evento):  # Agrega un evento con fecha y hora al historial
        self._historial.append((datetime.now(), evento))  # Guarda la tupla (momento, descripción)

    # ---------------- operaciones ----------------
    def confirmar(self):  # Pasa la reserva de PENDIENTE a CONFIRMADA
        if self._estado is not EstadoReserva.PENDIENTE:  # Solo se confirma lo que está pendiente
            raise OperacionNoPermitidaError(  # Error si ya estaba confirmada, cancelada o procesada
                f"La reserva {self.id} está {self._estado.value.lower()}; solo se confirman reservas pendientes."
            )
        try:  # Bloque try/except/else
            self._servicio.verificar_disponibilidad()  # Revisa que el servicio siga disponible
            costo_estimado = self._servicio.calcular_costo(self._duracion, **self._detalles)  # Calcula el costo base
        except ServicioNoDisponibleError as error:  # Si el servicio se deshabilitó después de crear la reserva...
            self._registrar_historial("Intento de confirmación fallido: servicio no disponible")  # ...se anota...
            raise ReservaError(f"No se pudo confirmar la reserva {self.id}.") from error  # ...y se encadena el error
        else:  # El else solo se ejecuta si el try terminó sin errores
            self._estado = EstadoReserva.CONFIRMADA  # Cambia el estado
            self._registrar_historial("Reserva confirmada")  # Lo anota en el historial
            return costo_estimado  # Devuelve el costo base estimado

    def cancelar(self, motivo):  # Cancela la reserva indicando el motivo
        if motivo is None or not str(motivo).strip():  # El motivo es obligatorio
            raise ParametroFaltanteError("Para cancelar una reserva hay que indicar el motivo.")  # Error si falta
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):  # No se cancela lo ya cancelado o cobrado
            raise OperacionNoPermitidaError(  # Error de operación no permitida
                f"La reserva {self.id} ya está {self._estado.value.lower()} y no se puede cancelar."
            )
        self._estado = EstadoReserva.CANCELADA  # Cambia el estado
        self._registrar_historial(f"Reserva cancelada. Motivo: {motivo}")  # Anota el motivo

    def procesar(self, impuesto=Servicio.IVA, descuento=None):  # Cobra la reserva (con IVA y descuento opcional)
        if self._estado is not EstadoReserva.CONFIRMADA:  # Solo se cobra lo que está confirmado
            raise OperacionNoPermitidaError(  # Error si está pendiente, cancelada o ya procesada
                f"La reserva {self.id} está {self._estado.value.lower()}; solo se procesan reservas confirmadas."
            )
        exito = False  # Bandera para saber, en el finally, si el cobro salió bien
        try:  # Bloque try/except/finally
            total = self._servicio.calcular_costo(self._duracion, impuesto, descuento, **self._detalles)  # Costo final
            self._costo_total = total  # Guarda el total cobrado
            self._estado = EstadoReserva.PROCESADA  # Cambia el estado
            exito = True  # Marca que el proceso salió bien
            return total  # Devuelve el total (el finally igual se ejecuta antes de salir)
        except CalculoInconsistenteError as error:  # Si el impuesto o descuento eran inválidos...
            raise ReservaError(f"No se pudo procesar el cobro de la reserva {self.id}.") from error  # ...se encadena
        finally:  # Se ejecuta SIEMPRE, haya error o no
            self._registrar_historial("Cobro procesado" if exito else "Intento de cobro fallido")  # Deja rastro del intento

    def describir(self):  # Implementación del método abstracto
        total = f" | Total {formato_pesos(self._costo_total)}" if self._costo_total else ""  # Total si ya se cobró
        return (f"{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} | "  # Quién y qué
                f"duración {self._duracion} | {self._estado.value}{total}")  # Duración, estado y total

    def validar(self):  # Implementación del método abstracto
        self._cliente.validar()  # Revalida al cliente
        self._servicio.validar()  # Revalida el servicio
        self._servicio.validar_parametros(self._duracion, **self._detalles)  # Revalida la solicitud
        return True  # La reserva es consistente

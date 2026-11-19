"""
servicios.py
------------
Clase abstracta Servicio y los tres servicios especializados de
Software FJ: reserva de salas, alquiler de equipos y asesorías.
"""

from abc import abstractmethod  # Para declarar los métodos que cada servicio debe implementar
from functools import singledispatchmethod  # Permite sobrecargar un método según el tipo del argumento

from entidades import EntidadBase  # Clase abstracta padre de todas las entidades
from excepciones import (  # Excepciones propias que usan los servicios
    ServicioInvalidoError,  # Datos de creación del servicio incorrectos
    ParametroFaltanteError,  # Falta un dato obligatorio
    DatoInvalidoError,  # Dato con tipo o rango incorrecto
    ServicioNoDisponibleError,  # El servicio está deshabilitado
    CalculoInconsistenteError,  # El costo no se pudo calcular o dio un valor ilógico
)
from utilidades import formato_pesos  # Para mostrar valores en pesos colombianos


class Servicio(EntidadBase):  # Sigue siendo abstracta porque no implementa todos los métodos abstractos
    """Servicio general que ofrece Software FJ."""

    IVA = 0.19  # IVA en Colombia (19 %), usado como impuesto por defecto

    def __init__(self, prefijo, nombre, tarifa):  # Datos comunes a todos los servicios
        if nombre is None or not str(nombre).strip():  # El nombre es obligatorio
            raise ParametroFaltanteError("Todo servicio necesita un nombre.")  # Error si viene vacío
        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)):  # La tarifa debe ser un número (bool no cuenta)
            raise ServicioInvalidoError(f"La tarifa debe ser numérica y llegó {tarifa!r}.")  # Error de tipo
        if tarifa <= 0:  # La tarifa no puede ser cero ni negativa
            raise ServicioInvalidoError(f"La tarifa debe ser mayor que cero y llegó {tarifa}.")  # Error de valor
        self._nombre = str(nombre).strip()  # Guarda el nombre sin espacios sobrantes
        self._tarifa = float(tarifa)  # Guarda la tarifa como número decimal
        self._disponible = True  # Todo servicio nace disponible
        super().__init__(prefijo)  # Asigna el id solo cuando todos los datos son válidos

    # ---------------- propiedades ----------------
    @property
    def nombre(self):  # Nombre del servicio (solo lectura)
        return self._nombre  # Devuelve el nombre

    @property
    def tarifa(self):  # Tarifa base (solo lectura)
        return self._tarifa  # Devuelve la tarifa

    @property
    def disponible(self):  # Indica si el servicio se puede reservar
        return self._disponible  # Devuelve True o False

    def habilitar(self):  # Vuelve a dejar el servicio disponible
        self._disponible = True  # Cambia el estado interno

    def deshabilitar(self):  # Deja el servicio fuera de uso (mantenimiento, agenda llena, etc.)
        self._disponible = False  # Cambia el estado interno

    def verificar_disponibilidad(self):  # Lanza un error si el servicio no se puede usar
        if not self._disponible:  # Si está deshabilitado...
            raise ServicioNoDisponibleError(f"El servicio {self.id} '{self._nombre}' no está disponible en este momento.")  # ...error
        return True  # Si está disponible, devuelve True

    # ---------------- validaciones de apoyo ----------------
    @staticmethod  # Método de apoyo que no depende del objeto
    def _validar_numero(valor, campo, minimo, maximo):  # Revisa que un valor sea numérico y esté dentro de un rango
        if valor is None:  # Si no llegó el dato...
            raise ParametroFaltanteError(f"Falta el dato '{campo}'.")  # ...es un parámetro faltante
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):  # Si no es número (o es True/False)...
            raise DatoInvalidoError(f"'{campo}' debe ser numérico y llegó {valor!r}.")  # ...es un dato inválido
        if not minimo <= valor <= maximo:  # Si está fuera del rango permitido...
            raise DatoInvalidoError(f"'{campo}' debe estar entre {minimo} y {maximo} y llegó {valor}.")  # ...también es inválido
        return valor  # Si todo está bien, devuelve el valor

    @staticmethod  # Revisa que un impuesto o descuento sea un porcentaje entre 0 y 1
    def _validar_porcentaje(valor, campo):
        try:  # Intenta convertir el valor a número decimal
            valor = float(valor)  # Si llega "abc" o una lista, aquí se produce ValueError o TypeError
        except (TypeError, ValueError) as error:  # Atrapa el error original de Python...
            raise CalculoInconsistenteError(f"El {campo} '{valor}' no es un número.") from error  # ...y lo encadena con uno propio
        if not 0 <= valor <= 1:  # Debe estar entre 0 (0 %) y 1 (100 %)
            raise CalculoInconsistenteError(f"El {campo} debe estar entre 0 y 1 (0 % a 100 %) y llegó {valor}.")  # Error de rango
        return valor  # Devuelve el porcentaje como decimal

    # ---------------- métodos abstractos (cada servicio los define) ----------------
    @abstractmethod  # Cada servicio calcula su costo base a su manera
    def costo_base(self, duracion, **detalles):
        """Costo del servicio antes de impuestos y descuentos."""

    @abstractmethod  # Cada servicio valida sus propios parámetros
    def validar_parametros(self, duracion, **detalles):
        """Revisa que la duración y los detalles de la solicitud sean válidos."""

    def validar(self):  # Implementa el método abstracto de EntidadBase con lo común a todo servicio
        if not self._nombre or self._tarifa <= 0:  # Revisa nombre y tarifa
            raise ServicioInvalidoError(f"El servicio {self.id} tiene datos inconsistentes.")  # Error si algo no cuadra
        return True  # El servicio es válido

    # ---------------- cálculo de costos (sobrecarga por parámetros opcionales) ----------------
    def calcular_costo(self, duracion, impuesto=None, descuento=None, **detalles):
        """
        Python no tiene sobrecarga como Java, así que se simula con parámetros opcionales:
          calcular_costo(d)              -> costo base
          calcular_costo(d, 0.19)        -> costo con impuesto
          calcular_costo(d, 0.19, 0.10)  -> costo con impuesto y descuento
        """
        self.validar_parametros(duracion, **detalles)  # Primero valida (llama a la versión de cada subclase: polimorfismo)
        try:  # Bloque protegido para el cálculo
            total = self.costo_base(duracion, **detalles)  # Costo base según el tipo de servicio
            if descuento is not None:  # Variante con descuento
                total *= 1 - self._validar_porcentaje(descuento, "descuento")  # Resta el porcentaje de descuento
            if impuesto is not None:  # Variante con impuesto
                total *= 1 + self._validar_porcentaje(impuesto, "impuesto")  # Suma el porcentaje de impuesto
        except TypeError as error:  # Si algún dato interno no permite operar...
            raise CalculoInconsistenteError(f"No se pudo calcular el costo de '{self._nombre}'.") from error  # ...se encadena
        if total < 0 or total != total:  # Un costo negativo o NaN (NaN es distinto de sí mismo) es ilógico
            raise CalculoInconsistenteError(f"El costo calculado para '{self._nombre}' es inválido: {total}.")  # Error de cálculo
        return round(total, 2)  # Devuelve el total redondeado a dos decimales

    # ---------------- cotizar (sobrecarga real según el tipo del argumento) ----------------
    @singledispatchmethod  # Versión por defecto: se usa cuando el tipo del argumento no está registrado
    def cotizar(self, solicitud):
        raise DatoInvalidoError(f"No se puede cotizar con un dato de tipo {type(solicitud).__name__}.")  # Tipo no soportado

    @cotizar.register(int)  # Variante 1: se pasa solo la duración como número entero...
    @cotizar.register(float)  # ...o decimal
    def _(self, solicitud):
        return self.calcular_costo(solicitud, self.IVA)  # Cotiza la duración con IVA y sin detalles extra

    @cotizar.register(dict)  # Variante 2: se pasa un diccionario con todos los datos de la solicitud
    def _(self, solicitud):
        datos = dict(solicitud)  # Copia el diccionario para no modificar el original
        if "duracion" not in datos:  # La duración es obligatoria
            raise ParametroFaltanteError("La cotización necesita el dato 'duracion'.")  # Error si falta
        duracion = datos.pop("duracion")  # Saca la duración del diccionario
        impuesto = datos.pop("impuesto", self.IVA)  # Saca el impuesto o usa el IVA por defecto
        descuento = datos.pop("descuento", None)  # Saca el descuento si lo hay
        return self.calcular_costo(duracion, impuesto, descuento, **datos)  # Lo que queda en datos son los detalles


class ReservaSala(Servicio):  # Servicio especializado 1: reserva de salas
    """Reserva de salas por horas."""

    def __init__(self, nombre, tarifa_hora, capacidad):  # Datos propios de una sala
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:  # Capacidad: entero positivo
            raise ServicioInvalidoError(f"La capacidad de la sala debe ser un entero positivo y llegó {capacidad!r}.")  # Error
        self._capacidad = capacidad  # Número máximo de personas
        super().__init__("SAL", nombre, tarifa_hora)  # El padre valida nombre y tarifa y asigna el id SAL-00X

    def validar_parametros(self, duracion, **detalles):  # Sobrescribe el método abstracto
        self._validar_numero(duracion, "duración en horas", 1, 12)  # Una sala se reserva de 1 a 12 horas
        self._validar_numero(detalles.get("asistentes"), "asistentes", 1, self._capacidad)  # No puede exceder la capacidad
        return True  # Parámetros correctos

    def costo_base(self, duracion, **detalles):  # Sobrescribe el método abstracto
        costo = self._tarifa * duracion  # Tarifa por hora × horas
        if duracion >= 8:  # Si es jornada completa...
            costo *= 0.90  # ...se aplica 10 % de descuento por jornada
        return costo  # Devuelve el costo base

    def describir(self):  # Sobrescribe el método abstracto
        return f"{self.id} | Sala '{self._nombre}' | {self._capacidad} personas | {formato_pesos(self._tarifa)}/hora"  # Descripción


class AlquilerEquipo(Servicio):  # Servicio especializado 2: alquiler de equipos
    """Alquiler de equipos por días."""

    PORCENTAJE_SEGURO = 0.05  # Seguro obligatorio del 5 % sobre el alquiler

    def __init__(self, nombre, tarifa_dia, tipo_equipo, unidades):  # Datos propios del equipo
        if tipo_equipo is None or not str(tipo_equipo).strip():  # El tipo de equipo es obligatorio
            raise ParametroFaltanteError("Hay que indicar el tipo de equipo.")  # Error si falta
        if isinstance(unidades, bool) or not isinstance(unidades, int) or unidades <= 0:  # Unidades: entero positivo
            raise ServicioInvalidoError(f"Las unidades disponibles deben ser un entero positivo y llegó {unidades!r}.")  # Error
        self._tipo_equipo = str(tipo_equipo).strip()  # Guarda el tipo (portátil, video beam, etc.)
        self._unidades = unidades  # Guarda cuántas unidades hay
        super().__init__("EQU", nombre, tarifa_dia)  # El padre valida y asigna el id EQU-00X

    def validar_parametros(self, duracion, **detalles):  # Sobrescribe el método abstracto
        self._validar_numero(duracion, "duración en días", 1, 30)  # Se alquila de 1 a 30 días
        self._validar_numero(detalles.get("cantidad", 1), "cantidad", 1, self._unidades)  # No más de las unidades existentes
        return True  # Parámetros correctos

    def costo_base(self, duracion, **detalles):  # Sobrescribe el método abstracto
        cantidad = detalles.get("cantidad", 1)  # Si no se indica, se alquila 1 unidad
        alquiler = self._tarifa * duracion * cantidad  # Tarifa diaria × días × unidades
        return alquiler * (1 + self.PORCENTAJE_SEGURO)  # Se suma el seguro del 5 %

    def describir(self):  # Sobrescribe el método abstracto
        return (f"{self.id} | Equipo '{self._nombre}' ({self._tipo_equipo}) | "  # Nombre y tipo
                f"{self._unidades} unidades | {formato_pesos(self._tarifa)}/día")  # Unidades y tarifa


class Asesoria(Servicio):  # Servicio especializado 3: asesorías especializadas
    """Asesoría especializada por horas, con nivel del asesor."""

    NIVELES = {"basico": 1.0, "intermedio": 1.25, "experto": 1.5}  # Multiplicador de la tarifa según el nivel
    RECARGO_PRESENCIAL = 50000  # Valor fijo de desplazamiento si la asesoría es presencial

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="intermedio"):  # Datos propios de la asesoría
        if especialidad is None or not str(especialidad).strip():  # La especialidad es obligatoria
            raise ParametroFaltanteError("La asesoría necesita una especialidad.")  # Error si falta
        nivel = str(nivel).strip().lower()  # Normaliza el nivel a minúsculas
        if nivel not in self.NIVELES:  # Solo se aceptan los niveles definidos
            raise ServicioInvalidoError(f"Nivel '{nivel}' no válido. Opciones: {', '.join(self.NIVELES)}.")  # Error
        self._especialidad = str(especialidad).strip()  # Guarda la especialidad
        self._nivel = nivel  # Guarda el nivel
        super().__init__("ASE", nombre, tarifa_hora)  # El padre valida y asigna el id ASE-00X

    def validar_parametros(self, duracion, **detalles):  # Sobrescribe el método abstracto
        self._validar_numero(duracion, "duración en horas", 1, 8)  # Una asesoría dura de 1 a 8 horas
        modalidad = detalles.get("modalidad", "virtual")  # Por defecto la asesoría es virtual
        if modalidad not in ("virtual", "presencial"):  # Solo hay dos modalidades
            raise DatoInvalidoError(f"Modalidad '{modalidad}' no válida: use 'virtual' o 'presencial'.")  # Error
        return True  # Parámetros correctos

    def costo_base(self, duracion, **detalles):  # Sobrescribe el método abstracto
        costo = self._tarifa * duracion * self.NIVELES[self._nivel]  # Tarifa × horas × multiplicador del nivel
        if detalles.get("modalidad") == "presencial":  # Si es presencial...
            costo += self.RECARGO_PRESENCIAL  # ...se suma el desplazamiento
        return costo  # Devuelve el costo base

    def describir(self):  # Sobrescribe el método abstracto
        return (f"{self.id} | Asesoría '{self._nombre}' | {self._especialidad} | "  # Nombre y especialidad
                f"nivel {self._nivel} | {formato_pesos(self._tarifa)}/hora")  # Nivel y tarifa

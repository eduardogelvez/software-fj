"""
entidades.py
------------
Clase abstracta EntidadBase (de la que heredan cliente, servicios y
reservas) y la clase Cliente con sus validaciones.
"""

from abc import ABC, abstractmethod  # ABC permite crear clases abstractas; abstractmethod marca métodos obligatorios
from datetime import datetime  # Para guardar la fecha y hora en que se crea cada entidad
import re  # Expresiones regulares para validar nombre, documento, correo y teléfono

from excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores propios que lanza este módulo


class EntidadBase(ABC):  # Clase abstracta: no se puede crear un objeto EntidadBase directamente
    """Representa cualquier entidad del sistema (cliente, servicio o reserva)."""

    _contadores = {}  # Diccionario compartido: guarda el último consecutivo usado por cada prefijo

    def __init__(self, prefijo):  # El prefijo indica el tipo de entidad: CLI, SAL, EQU, ASE o RES
        consecutivo = EntidadBase._contadores.get(prefijo, 0) + 1  # Toma el último número de ese prefijo y le suma 1
        EntidadBase._contadores[prefijo] = consecutivo  # Guarda el nuevo número para la siguiente entidad
        self._id = f"{prefijo}-{consecutivo:03d}"  # Arma el identificador con 3 dígitos, ej: CLI-001
        self._fecha_creacion = datetime.now()  # Guarda el momento exacto en que se creó

    @property  # Permite leer el id como si fuera un atributo, pero no cambiarlo (encapsulación)
    def id(self):
        return self._id  # Devuelve el identificador único

    @property  # Fecha de creación de solo lectura
    def fecha_creacion(self):
        return self._fecha_creacion  # Devuelve el objeto datetime

    @abstractmethod  # Toda subclase está obligada a definir cómo se describe
    def describir(self):
        """Devuelve un texto que describe la entidad."""

    @abstractmethod  # Toda subclase está obligada a definir cómo se valida
    def validar(self):
        """Verifica que los datos de la entidad sean correctos."""

    def __str__(self):  # Lo que se muestra al hacer print(entidad)
        return self.describir()  # Reutiliza describir(), que cada subclase implementa a su manera (polimorfismo)


class Cliente(EntidadBase):  # Cliente hereda de EntidadBase
    """Cliente de Software FJ con sus datos personales protegidos."""

    PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")  # Solo letras y espacios, entre 3 y 60 caracteres
    PATRON_DOCUMENTO = re.compile(r"^\d{6,10}$")  # Cédula colombiana: solo números, entre 6 y 10 dígitos
    PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")  # Algo@dominio.ext
    PATRON_TELEFONO = re.compile(r"^3\d{9}$")  # Celular colombiano: 10 dígitos y empieza por 3

    def __init__(self, documento, nombre, correo, telefono):  # Recibe los cuatro datos del cliente
        self.__documento = self._validar_documento(documento)  # Atributo privado (doble guion bajo): no se toca desde afuera
        self.nombre = nombre  # Usa el setter de nombre, que valida antes de guardar
        self.correo = correo  # Usa el setter de correo, que valida antes de guardar
        self.telefono = telefono  # Usa el setter de teléfono, que valida antes de guardar
        super().__init__("CLI")  # Solo si todo es válido se asigna el id; así un cliente inválido no gasta consecutivo

    # ---------------- validaciones internas ----------------
    @staticmethod  # No necesita self: solo revisa que un valor no venga vacío
    def _exigir(valor, campo):
        if valor is None or not str(valor).strip():  # None, "" o "   " cuentan como vacío
            raise ParametroFaltanteError(f"El campo '{campo}' del cliente es obligatorio.")  # Error de dato faltante
        return str(valor).strip()  # Devuelve el valor como texto y sin espacios a los lados

    def _validar_documento(self, documento):  # Revisa que el documento tenga formato de cédula
        documento = self._exigir(documento, "documento")  # Primero verifica que no esté vacío
        if not self.PATRON_DOCUMENTO.match(documento):  # Si no son entre 6 y 10 números...
            raise ClienteInvalidoError(f"Documento '{documento}' inválido: deben ser de 6 a 10 dígitos.")  # ...lanza el error
        return documento  # Si pasa la validación, lo devuelve limpio

    # ---------------- propiedades (getters y setters) ----------------
    @property  # El documento solo se puede leer; no tiene setter porque no debe cambiar
    def documento(self):
        return self.__documento  # Devuelve el documento completo (uso interno del sistema)

    @property  # Versión segura del documento para mostrar en pantalla
    def documento_enmascarado(self):
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]  # Oculta todo menos los últimos 4 dígitos

    @property  # Getter del nombre
    def nombre(self):
        return self.__nombre  # Devuelve el nombre guardado

    @nombre.setter  # Setter del nombre: se ejecuta cada vez que se hace cliente.nombre = ...
    def nombre(self, valor):
        valor = self._exigir(valor, "nombre")  # Verifica que no venga vacío
        if not self.PATRON_NOMBRE.match(valor):  # Verifica que solo tenga letras y espacios
            raise ClienteInvalidoError(f"Nombre '{valor}' inválido: solo letras y espacios (3 a 60).")  # Error si tiene números o símbolos
        self.__nombre = valor.title()  # Guarda el nombre con mayúscula inicial en cada palabra

    @property  # Getter del correo
    def correo(self):
        return self.__correo  # Devuelve el correo guardado

    @correo.setter  # Setter del correo con validación
    def correo(self, valor):
        valor = self._exigir(valor, "correo")  # Verifica que no venga vacío
        if not self.PATRON_CORREO.match(valor):  # Verifica el formato usuario@dominio.ext
            raise ClienteInvalidoError(f"Correo '{valor}' inválido.")  # Error si el formato no cuadra
        self.__correo = valor.lower()  # Guarda el correo en minúsculas

    @property  # Getter del teléfono
    def telefono(self):
        return self.__telefono  # Devuelve el teléfono guardado

    @telefono.setter  # Setter del teléfono con validación
    def telefono(self, valor):
        valor = self._exigir(valor, "teléfono")  # Verifica que no venga vacío
        if not self.PATRON_TELEFONO.match(valor):  # Debe ser un celular colombiano de 10 dígitos
            raise ClienteInvalidoError(f"Teléfono '{valor}' inválido: debe ser un celular de 10 dígitos que empiece por 3.")  # Error
        self.__telefono = valor  # Guarda el teléfono

    # ---------------- métodos abstractos implementados ----------------
    def validar(self):  # Implementación obligatoria del método abstracto
        """Vuelve a comprobar todos los datos del cliente."""
        self._validar_documento(self.__documento)  # Revalida el documento
        self.nombre = self.__nombre  # Pasa de nuevo por el setter, que valida
        self.correo = self.__correo  # Revalida el correo
        self.telefono = self.__telefono  # Revalida el teléfono
        return True  # Si no se lanzó ninguna excepción, el cliente es válido

    def describir(self):  # Implementación obligatoria del método abstracto
        return f"{self.id} | {self.nombre} | Doc. {self.documento_enmascarado} | {self.correo}"  # Datos sensibles enmascarados

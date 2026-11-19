"""
sistema.py
----------
Clase SistemaSoftwareFJ: guarda clientes, servicios y reservas en listas
internas (sin base de datos) y ejecuta cada operación atrapando los
errores para que el programa nunca se detenga.
"""

from entidades import Cliente  # Clase Cliente
from servicios import ReservaSala, AlquilerEquipo, Asesoria  # Los tres servicios concretos
from reserva import Reserva  # Clase Reserva
from excepciones import (  # Excepciones que el sistema lanza o atrapa
    SoftwareFJError,  # Base: atrapa cualquier error propio
    ClienteInvalidoError,  # Para clientes duplicados
    ServicioInvalidoError,  # Para tipos de servicio inexistentes
    ParametroFaltanteError,  # Para datos incompletos al crear servicios
    EntidadNoEncontradaError,  # Para búsquedas sin resultado
)
from utilidades import obtener_logger, registrar_error, formato_pesos  # Logs y formato de pesos


class SistemaSoftwareFJ:
    """Punto central que administra toda la información en memoria."""

    TIPOS_SERVICIO = {  # Relaciona el nombre del tipo con la clase que lo crea
        "sala": ReservaSala,  # "sala" crea un objeto ReservaSala
        "equipo": AlquilerEquipo,  # "equipo" crea un objeto AlquilerEquipo
        "asesoria": Asesoria,  # "asesoria" crea un objeto Asesoria
    }

    def __init__(self):  # Crea el sistema vacío
        self.__clientes = []  # Lista privada de clientes
        self.__servicios = []  # Lista privada de servicios
        self.__reservas = []  # Lista privada de reservas
        self._log = obtener_logger()  # Logger que escribe en logs/software_fj.log
        self._log.info("========== Inicio de sesión del sistema Software FJ ==========")  # Marca el inicio en el log

    # ---------------- apoyo interno ----------------
    def _manejar_error(self, operacion, error):  # Registra el error y lo muestra en pantalla sin detener el programa
        registrar_error(self._log, operacion, error)  # Lo escribe en el log con toda su cadena de causas
        print(f"   ✗ {operacion} falló: {error}")  # Mensaje principal en consola
        causa = error.__cause__  # Revisa si el error fue encadenado
        while causa is not None:  # Muestra cada causa en una línea aparte
            print(f"       causado por: {causa}")  # Causa en consola
            causa = causa.__cause__  # Pasa a la siguiente causa

    def _buscar_cliente(self, documento):  # Busca un cliente por documento; lanza error si no existe
        for cliente in self.__clientes:  # Recorre la lista de clientes
            if cliente.documento == str(documento).strip():  # Compara documentos como texto
                return cliente  # Lo encontró
        raise EntidadNoEncontradaError(f"No existe un cliente con documento '{documento}'.")  # No lo encontró

    def _buscar_servicio(self, codigo):  # Busca un servicio por código (SAL-001, EQU-001...)
        for servicio in self.__servicios:  # Recorre la lista de servicios
            if servicio.id == codigo:  # Compara el código
                return servicio  # Lo encontró
        raise EntidadNoEncontradaError(f"No existe el servicio '{codigo}'.")  # No lo encontró

    def _buscar_reserva(self, codigo):  # Busca una reserva por código (RES-001...)
        for reserva in self.__reservas:  # Recorre la lista de reservas
            if reserva.id == codigo:  # Compara el código
                return reserva  # La encontró
        raise EntidadNoEncontradaError(f"No existe la reserva '{codigo}'.")  # No la encontró

    # ---------------- clientes ----------------
    def registrar_cliente(self, documento, nombre, correo, telefono):  # Crea y guarda un cliente
        try:  # try/except/else
            if any(c.documento == str(documento).strip() for c in self.__clientes):  # ¿Ya existe ese documento?
                raise ClienteInvalidoError(f"Ya existe un cliente registrado con el documento '{documento}'.")  # Duplicado
            cliente = Cliente(documento, nombre, correo, telefono)  # Crea el cliente (aquí se validan los datos)
        except SoftwareFJError as error:  # Cualquier error propio...
            self._manejar_error("Registro de cliente", error)  # ...se registra y se muestra
            return None  # Devuelve None para indicar que no se registró
        else:  # Solo si no hubo error
            self.__clientes.append(cliente)  # Lo agrega a la lista
            self._log.info(f"Cliente registrado: {cliente.id} - {cliente.nombre}")  # Evento en el log
            print(f"   ✓ Cliente registrado: {cliente}")  # Confirmación en consola
            return cliente  # Devuelve el cliente creado

    # ---------------- servicios ----------------
    def agregar_servicio(self, tipo, **datos):  # Crea un servicio del tipo indicado con los datos recibidos
        try:  # try/except/else
            clase = self.TIPOS_SERVICIO.get(str(tipo).strip().lower())  # Busca la clase correspondiente al tipo
            if clase is None:  # Si el tipo no existe...
                raise ServicioInvalidoError(  # ...se lanza el error con las opciones válidas
                    f"El tipo de servicio '{tipo}' no existe. Opciones: {', '.join(self.TIPOS_SERVICIO)}."
                )
            try:  # try anidado para detectar argumentos faltantes o sobrantes
                servicio = clase(**datos)  # Crea el servicio con los datos recibidos
            except TypeError as error:  # Python lanza TypeError si faltan o sobran argumentos en el constructor
                raise ParametroFaltanteError(f"Datos incompletos para crear un servicio de tipo '{tipo}'.") from error  # Encadena
        except SoftwareFJError as error:  # Cualquier error propio...
            self._manejar_error("Creación de servicio", error)  # ...se registra y se muestra
            return None  # No se creó el servicio
        else:  # Solo si no hubo error
            self.__servicios.append(servicio)  # Lo agrega a la lista
            self._log.info(f"Servicio creado: {servicio.id} - {servicio.nombre}")  # Evento en el log
            print(f"   ✓ Servicio creado: {servicio}")  # Confirmación en consola
            return servicio  # Devuelve el servicio creado

    def cambiar_disponibilidad(self, codigo, disponible):  # Habilita o deshabilita un servicio
        try:  # try/except/else
            servicio = self._buscar_servicio(codigo)  # Busca el servicio
        except SoftwareFJError as error:  # Si no existe...
            self._manejar_error("Cambio de disponibilidad", error)  # ...se registra
            return False  # No se pudo cambiar
        else:  # Si lo encontró
            servicio.habilitar() if disponible else servicio.deshabilitar()  # Cambia el estado según el parámetro
            estado = "habilitado" if disponible else "deshabilitado"  # Texto para el mensaje
            self._log.warning(f"Servicio {codigo} {estado}")  # Se registra como advertencia porque afecta reservas
            print(f"   ✓ Servicio {codigo} {estado}")  # Confirmación en consola
            return True  # Cambio exitoso

    def cotizar_servicio(self, codigo, solicitud):  # Cotiza usando el método sobrecargado cotizar()
        try:  # try/except/else
            servicio = self._buscar_servicio(codigo)  # Busca el servicio
            valor = servicio.cotizar(solicitud)  # La variante que se ejecuta depende del tipo de 'solicitud'
        except SoftwareFJError as error:  # Si algo falla...
            self._manejar_error("Cotización", error)  # ...se registra
            return None  # Sin cotización
        else:  # Si todo salió bien
            self._log.info(f"Cotización de {codigo} con {type(solicitud).__name__}: {formato_pesos(valor)}")  # Evento
            print(f"   ✓ Cotización de {codigo}: {formato_pesos(valor)} (IVA incluido)")  # Resultado en consola
            return valor  # Devuelve el valor cotizado

    # ---------------- reservas ----------------
    def crear_reserva(self, documento_cliente, codigo_servicio, duracion, **detalles):  # Crea una reserva pendiente
        try:  # try/except/else
            cliente = self._buscar_cliente(documento_cliente)  # El cliente debe existir
            servicio = self._buscar_servicio(codigo_servicio)  # El servicio debe existir
            servicio.verificar_disponibilidad()  # El servicio debe estar disponible
            reserva = Reserva(cliente, servicio, duracion, **detalles)  # Crea la reserva (valida parámetros)
        except SoftwareFJError as error:  # Cualquier error propio...
            self._manejar_error("Creación de reserva", error)  # ...se registra y se muestra
            return None  # No se creó
        else:  # Solo si no hubo error
            self.__reservas.append(reserva)  # La agrega a la lista
            self._log.info(f"Reserva creada: {reserva.id} - {cliente.nombre} -> {servicio.nombre}")  # Evento
            print(f"   ✓ Reserva creada: {reserva}")  # Confirmación en consola
            return reserva  # Devuelve la reserva

    def confirmar_reserva(self, codigo):  # Confirma una reserva pendiente
        try:  # try/except/else
            reserva = self._buscar_reserva(codigo)  # Busca la reserva
            costo = reserva.confirmar()  # Intenta confirmarla
        except SoftwareFJError as error:  # Si falla...
            self._manejar_error("Confirmación de reserva", error)  # ...se registra
            return False  # No se confirmó
        else:  # Si salió bien
            self._log.info(f"Reserva confirmada: {codigo} (costo base {formato_pesos(costo)})")  # Evento
            print(f"   ✓ Reserva {codigo} confirmada. Costo base: {formato_pesos(costo)}")  # Confirmación
            return True  # Confirmada

    def cancelar_reserva(self, codigo, motivo):  # Cancela una reserva con su motivo
        try:  # try/except/else
            reserva = self._buscar_reserva(codigo)  # Busca la reserva
            reserva.cancelar(motivo)  # Intenta cancelarla
        except SoftwareFJError as error:  # Si falla...
            self._manejar_error("Cancelación de reserva", error)  # ...se registra
            return False  # No se canceló
        else:  # Si salió bien
            self._log.info(f"Reserva cancelada: {codigo}. Motivo: {motivo}")  # Evento
            print(f"   ✓ Reserva {codigo} cancelada ({motivo})")  # Confirmación
            return True  # Cancelada

    def procesar_reserva(self, codigo, impuesto=0.19, descuento=None):  # Cobra una reserva confirmada
        self._log.debug(f"Inicio de procesamiento de {codigo}")  # Deja rastro del inicio del intento
        try:  # try/except/else/finally (los cuatro bloques juntos)
            reserva = self._buscar_reserva(codigo)  # Busca la reserva
            total = reserva.procesar(impuesto, descuento)  # Intenta cobrarla
        except SoftwareFJError as error:  # Si falla...
            self._manejar_error("Procesamiento de reserva", error)  # ...se registra
            return None  # Sin cobro
        else:  # Si salió bien
            self._log.info(f"Reserva procesada: {codigo} - total {formato_pesos(total)}")  # Evento
            print(f"   ✓ Reserva {codigo} procesada. Total cobrado: {formato_pesos(total)}")  # Confirmación
            return total  # Devuelve el total cobrado
        finally:  # Siempre se ejecuta
            self._log.debug(f"Fin de procesamiento de {codigo}")  # Deja rastro del cierre del intento

    # ---------------- reporte ----------------
    def resumen(self):  # Muestra un resumen de todo lo que hay en memoria
        print("\n" + "=" * 70)  # Línea separadora
        print("RESUMEN DEL SISTEMA SOFTWARE FJ")  # Título
        print("=" * 70)  # Línea separadora
        print(f"Clientes registrados: {len(self.__clientes)}")  # Cantidad de clientes
        for cliente in self.__clientes:  # Lista cada cliente
            print(f"   {cliente}")  # Usa __str__ -> describir()
        print(f"Servicios disponibles: {len(self.__servicios)}")  # Cantidad de servicios
        for servicio in self.__servicios:  # Lista cada servicio (polimorfismo: cada uno se describe distinto)
            print(f"   {servicio}")  # Usa __str__ -> describir()
        print(f"Reservas: {len(self.__reservas)}")  # Cantidad de reservas
        for reserva in self.__reservas:  # Lista cada reserva
            print(f"   {reserva}")  # Usa __str__ -> describir()
        total = sum(r.costo_total or 0 for r in self.__reservas)  # Suma lo cobrado (None cuenta como 0)
        print(f"Total facturado: {formato_pesos(total)}")  # Total en pesos
        print("=" * 70)  # Línea separadora
        self._log.info(f"Resumen generado - facturado {formato_pesos(total)}")  # Evento en el log

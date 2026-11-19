"""
utilidades.py
-------------
Configuración del archivo de logs y funciones de apoyo que usan
varios módulos del sistema.
"""

import logging  # Módulo estándar de Python para escribir registros (logs)
import os  # Permite armar rutas de carpetas y archivos sin importar el sistema operativo

CARPETA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # Carpeta "logs" junto a este archivo
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")  # Ruta completa del archivo de logs
os.makedirs(CARPETA_LOGS, exist_ok=True)  # Crea la carpeta si no existe; si ya existe no hace nada


def obtener_logger(nombre="SoftwareFJ"):  # Devuelve el logger del sistema, configurado una sola vez
    """Entrega el logger que escribe en logs/software_fj.log."""
    logger = logging.getLogger(nombre)  # Pide a Python el logger con ese nombre (si existe lo reutiliza)
    if not logger.handlers:  # Solo se configura la primera vez, para no duplicar líneas en el archivo
        logger.setLevel(logging.DEBUG)  # Registra todos los niveles: DEBUG, INFO, WARNING, ERROR y CRITICAL
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")  # Escribe al final del archivo, con tildes y ñ
        formato = logging.Formatter(  # Define cómo se ve cada línea del log
            "%(asctime)s | %(levelname)-8s | %(message)s",  # Fecha | nivel | mensaje
            datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha: 2026-11-19 10:30:00
        )
        manejador.setFormatter(formato)  # Le aplica el formato al manejador del archivo
        logger.addHandler(manejador)  # Conecta el manejador al logger
        logger.propagate = False  # Evita que los mensajes también salgan por la consola
    return logger  # Devuelve el logger listo para usar


def registrar_error(logger, operacion, error):  # Escribe un error en el log incluyendo toda su cadena de causas
    """Registra el error y, si fue encadenado con 'raise ... from', también sus causas."""
    mensaje = f"{operacion} | {type(error).__name__}: {error}"  # Línea principal: operación, tipo de error y mensaje
    causa = error.__cause__  # __cause__ guarda la excepción original cuando se usó 'raise ... from'
    while causa is not None:  # Recorre la cadena completa de errores (puede tener varios niveles)
        mensaje += f" <- causado por {type(causa).__name__}: {causa}"  # Agrega cada causa al mensaje
        causa = causa.__cause__  # Pasa a la causa anterior
    logger.error(mensaje)  # Escribe todo en el archivo con nivel ERROR


def formato_pesos(valor):  # Convierte un número a texto con formato de pesos colombianos
    """Ejemplo: 1234567.8 -> '$1.234.568'."""
    return f"${valor:,.0f}".replace(",", ".")  # Usa separador de miles con coma y luego lo cambia por punto

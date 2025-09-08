class ValidationError(Exception):
    """400: Alguno de los campos no está  presente en la solicitud, o no tiene el formato esperado."""
    pass

class InvalidTokenError(Exception):
    """401: El token no es válido o está vencido."""
    pass

class NoTokenError(Exception):
    """403: El Token no está en la solicitud."""

class InvalidRouteDatesError(Exception):
    "412: Las fechas del trayecto no son validas."
    pass

class InvalidExpiredAtError(Exception):
    "412: La fecha de expiración no es válida."
    pass

class ConflictError(Exception):
    "412: El usuario ya tiene una publicación para la misma fecha ."
    pass

class ServiceCommunicationError(Exception):
    """503: El servicio está temporalmente fuera de servicio."""
    pass
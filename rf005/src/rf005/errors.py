class ServiceCommunicationError(Exception):
    """Excepción para errores de comunicación con otros servicios."""
    pass

class EntityNotFoundError(Exception):
    """Excepción para cuando una entidad no se encuentra."""
    pass

class AuthorizationError(Exception):
    """Excepción para errores de autorización"""
    pass

class InvalidTokenError(Exception):
    """Excepción para cuando el token no es válido o ha expirado"""
    pass
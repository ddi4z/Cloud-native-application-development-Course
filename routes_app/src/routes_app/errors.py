class TrayectoError(Exception):
    """Clase base para excepciones relacionadas con Trayectos."""
    pass

class TrayectoNotFoundError(TrayectoError):
    """Excepción para cuando un trayecto no se encuentra en el repositorio."""
    pass

class FlightIdAlreadyExistsError(TrayectoError):
    """Excepción para cuando se intenta crear un trayecto con un flightId que ya existe."""
    pass
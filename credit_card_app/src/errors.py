class BaseError(Exception):
    @property
    def message(self):
        return "Ha ocurrido un error inesperado."

class InvalidTokenError(BaseError):
    @property
    def message(self):
        return "El token no es válido o está vencido."

class MissingTokenError(BaseError):
    @property
    def message(self):
        return "No hay token en la solicitud."

class MalformedRequestError(BaseError):
    def __init__(self, details=""):
        self._message = f"La solicitud es incorrecta. {details}".strip()
    
    @property
    def message(self):
        return self._message

class CardAlreadyExistsError(BaseError):
    @property
    def message(self):
        return "El usuario ya había almacenado la misma tarjeta de crédito."

class CardExpiredError(BaseError):
    @property
    def message(self):
        return "La tarjeta de crédito ya está vencida."

class ServiceCommunicationError(BaseError):
    def __init__(self, details=""):
        self._message = f"Error de comunicación con un servicio externo. {details}".strip()
        
    @property
    def message(self):
        return self._message

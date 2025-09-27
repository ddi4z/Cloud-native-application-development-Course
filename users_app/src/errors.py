class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""

    pass


class InvalidCredentialsError(Exception):
    """Exception raised when the provided credentials are invalid."""

    pass


class MissingUserInformationError(Exception):
    """Exception raised when the provided user information is incomplete."""

    pass


class MissingTokenError(Exception):
    """Exception raised when the authentication token is missing."""

    pass


class InvalidTokenError(Exception):
    """Exception raised when the provided authentication token is invalid."""

    pass


class UserAlreadyExistsError(Exception):
    """Exception raised when trying to create a user that already exists."""

    pass


class UnauthorizedUserStatusError(Exception):
    """Exception raised when the user status does not allow the requested operation."""

    pass

class IntegrationError(Exception):
    """Exception raised when there is an integration error with an external service."""

    pass

class UnavailableService(Exception):
    """Exception raised when an external service is unavailable."""

    pass
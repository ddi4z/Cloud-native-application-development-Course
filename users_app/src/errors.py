class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""
    pass


class InvalidCredentialsError(Exception):
    """Exception raised when the provided credentials are invalid."""
    pass


class MissingTokenError(Exception):
    """Exception raised when the authentication token is missing."""
    pass

class InvalidTokenError(Exception):
    """Exception raised when the provided authentication token is invalid."""
    pass
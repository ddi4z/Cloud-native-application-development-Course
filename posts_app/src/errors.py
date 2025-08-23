class MissingPostInformationError(Exception):
    """Exception raised when the provided user information is incomplete."""

    pass


class InvalidExpirationDate(Exception):
    """Exception raised when the provided expiration date is not in the future."""

    pass


class PostNotFoundError(Exception):
    """Exception raised when a post is not found."""

    pass


class InvalidCredentialsError(Exception):
    """Exception raised when the provided credentials are invalid."""

    pass


class MissingIdError(Exception):
    """Exception raised when the post id is missing."""

    pass

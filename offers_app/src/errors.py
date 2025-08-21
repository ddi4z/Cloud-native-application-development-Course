class OfferNotFoundError(Exception):
    """Exception raised when an offer is not found."""

    pass


class InvalidFieldInOfferError(Exception):
    """Exception raised when a required field is missing."""

    pass


class PreconditionOfferFailedError(Exception):
    """Exception raised when a precondition for an offer fails."""

    pass

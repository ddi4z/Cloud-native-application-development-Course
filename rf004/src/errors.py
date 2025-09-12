class UnauthorizedError(Exception):
    """Exception raised when a user is not authenticated."""
    pass

class PostNotFoundError(Exception):
    """Exception raised when a post is not found."""
    pass

class PostExpiredError(Exception):
    """Exception raised when a post has expired."""
    pass

class OfferOnOwnPostError(Exception):
    """Exception raised when a user tries to create an offer on their own post."""
    pass

class InvalidOfferInputError(Exception):
    """Exception raised when the offer input is invalid."""
    pass

class UnavailableService(Exception):
    """Exception raised when some service is unavailable."""
    pass

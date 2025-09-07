class UnauthorizedError(Exception):
    """401: Missing/invalid auth."""
    pass

class ValidationError(Exception):
    """400: Bad input that violates business rules."""
    pass

class ConflictError(Exception):
    """409: Uniqueness / duplicate conflict."""
    pass

class DependencyError(Exception):
    """502: Downstream service or adapter failure."""
    pass
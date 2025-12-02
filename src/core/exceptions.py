class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedError(AppException):
    """Authentication required."""
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """Access denied."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    """Conflict with current state."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)


class ValidationError(AppException):
    """Business validation error."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

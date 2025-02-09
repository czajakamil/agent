class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)

class ConfigError(AppError):
    """Configuration related errors."""
    pass

class ServiceError(AppError):
    """Service related errors."""
    pass

class APIError(AppError):
    """API related errors."""
    pass

class IntegrationError(AppError):
    """External integration related errors."""
    pass 
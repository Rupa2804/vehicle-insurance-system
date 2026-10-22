class AppError(Exception):
    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


class ConflictError(AppError):
    pass


class InvalidStateTransitionError(AppError):
    pass
class CategoryNotFoundError(Exception):
    pass


class CategoryInUseError(Exception):
    pass


class CategoryAlreadyExistsError(Exception):
    pass


class TagNotFoundError(Exception):
    pass


class TagAlreadyExistsError(Exception):
    pass


class ExpenseNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AccessTokenExpiredError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass

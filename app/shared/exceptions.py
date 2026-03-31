from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    # Safely convert body to string if not serializable
    body = exc.body
    if body and not isinstance(body, (dict, list, str, int, float, bool, type(None))):
        body = str(body)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body},
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )

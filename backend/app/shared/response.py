from typing import Any
from fastapi.responses import JSONResponse

def build_success_response(
    data: Any = None, 
    message: str = "Operation completed successfully", 
    status_code: int = 200
) -> JSONResponse:
    """
    Returns a standardized API response indicating success.
    Merges data keys directly into the root dict if data is a dictionary.
    """
    content = {
        "status": "success",
        "message": message
    }
    if data:
        if isinstance(data, dict):
            content.update(data)
        else:
            content["data"] = data
    return JSONResponse(content=content, status_code=status_code)

def build_failure_response(
    message: str = "An error occurred", 
    error: Any = None, 
    status_code: int = 400
) -> JSONResponse:
    """
    Returns a standardized API response indicating failure.
    """
    content = {
        "status": "failed",
        "message": message
    }
    if error:
        content["error_details"] = error
    return JSONResponse(content=content, status_code=status_code)

def build_validation_error_response(
    message: str = "Validation failed", 
    errors: Any = None
) -> JSONResponse:
    """
    Returns a standardized validation error response.
    """
    content = {
        "status": "failed",
        "message": message
    }
    if errors:
        content["errors"] = errors
    return JSONResponse(content=content, status_code=422)

# Backwards compatibility aliases for legacy imports in other agent modules
def success_response(
    data: Any = None, 
    message: str = "Operation completed successfully", 
    status_code: int = 200
) -> JSONResponse:
    return build_success_response(data=data, message=message, status_code=status_code)

def error_response(
    message: str = "An error occurred", 
    error: Any = None, 
    status_code: int = 400
) -> JSONResponse:
    return build_failure_response(message=message, error=error, status_code=status_code)


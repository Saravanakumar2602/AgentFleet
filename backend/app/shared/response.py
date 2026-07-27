from typing import Any, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class APIResponseSchema(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None

def success_response(
    data: Any = None, 
    message: str = "Operation completed successfully", 
    status_code: int = 200
) -> JSONResponse:
    """
    Returns a standardized success response.
    """
    response_data = APIResponseSchema(
        success=True,
        message=message,
        data=data,
        error=None
    ).model_dump()
    return JSONResponse(content=response_data, status_code=status_code)

def error_response(
    message: str = "An error occurred", 
    error: Any = None, 
    status_code: int = 400
) -> JSONResponse:
    """
    Returns a standardized error response.
    """
    response_data = APIResponseSchema(
        success=False,
        message=message,
        data=None,
        error=error
    ).model_dump()
    return JSONResponse(content=response_data, status_code=status_code)

from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


def ok(message: str, data: Any = None) -> APIResponse:
    return APIResponse(success=True, message=message, data=data)


# def fail(message: str, error: str = None) -> APIResponse:
#     return APIResponse(success=False, message=message, error=error)

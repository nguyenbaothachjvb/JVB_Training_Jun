import logging
from fastapi import APIRouter
from schemas.response_schema import APIResponse, ok

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ping", response_model=APIResponse, status_code=200)
def ping():
    logger.debug("Health check /ping được gọi")
    return ok(message="pong")

@router.get("/", response_model=APIResponse, status_code=200)
def ping():
    logger.debug("Hello")
    return ok(message="Hello")
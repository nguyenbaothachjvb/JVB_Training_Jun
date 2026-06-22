import logging
import logging.config
from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from auth_api_demo.routers.health import router as health_router
from auth_api_demo.routers.auth import router as auth_router
from auth_api_demo.routers.users import router as users_router

# ── Cấu hình Logging ──────────────────────────────────────────────────────────
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def _serialize(obj):
    """Chuyển đổi kiểu dữ liệu không JSON-serializable (datetime, date, ...) sang string."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Kiểu {type(obj)} không serialize được")


def json_response(content: dict, status_code: int = 200) -> JSONResponse:
    """JSONResponse có hỗ trợ datetime từ MySQL."""
    import json
    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(content, default=_serialize)),
    )


# ── Khởi tạo app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="JVB Training – Auth API",
    description="Demo API với cơ chế Auth JWT chuẩn (access + refresh token).",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)


# ── Global Exception Handlers ─────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Bắt tất cả HTTPException và trả về đúng REST envelope."""
    logger.warning(
        "HTTPException %s tại %s – %s", exc.status_code, request.url.path, exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
            "error": f"HTTP_{exc.status_code}",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Bắt lỗi validate Pydantic (422) và trả về đúng REST envelope."""
    errors = exc.errors()
    first = errors[0] if errors else {}
    field = " → ".join(str(loc) for loc in first.get("loc", []))
    msg = first.get("msg", "Dữ liệu không hợp lệ")

    logger.warning(
        "ValidationError tại %s – field=%s, msg=%s", request.url.path, field, msg
    )
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": f"Dữ liệu đầu vào không hợp lệ: {field} – {msg}",
            "data": None,
            "error": "VALIDATION_ERROR",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Bắt mọi lỗi không mong đợi, tránh lộ stack trace ra client."""
    logger.error(
        "Lỗi không xử lý tại %s – %s", request.url.path, str(exc), exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Đã xảy ra lỗi hệ thống, vui lòng thử lại sau",
            "data": None,
            "error": "INTERNAL_SERVER_ERROR",
        },
    )
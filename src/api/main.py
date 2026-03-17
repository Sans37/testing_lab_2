from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import logging

# 👇 Добавляем этот импорт
from src.api.v2.routers import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nady Bakery API")

# Middleware для проверки read-only
@app.middleware("http")
async def check_read_only(request, call_next):
    if os.getenv("READ_ONLY", "false").lower() == "true":
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Write operation not allowed on read-only replica",
                    "instance": os.getenv("APP_INSTANCE", "unknown")
                }
            )
    return await call_next(request)

# 👇 Подключаем все роутеры API v2
app.include_router(api_router, prefix="/api/v2")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Nady Bakery API",
        "instance": os.getenv("APP_INSTANCE", "unknown"),
        "db_role": os.getenv("DB_ROLE", "unknown"),
        "read_only": os.getenv("READ_ONLY", "false")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Nady Bakery API",
        "instance": os.getenv("APP_INSTANCE", "unknown")
    }

@app.get("/instance-info")
async def instance_info():
    return {
        "instance": os.getenv("APP_INSTANCE", "unknown"),
        "db_role": os.getenv("DB_ROLE", "unknown"),
        "read_only": os.getenv("READ_ONLY", "false")
    }

# Эти тестовые эндпоинты можно оставить или удалить
# Они не конфликтуют с основными роутами

# Middleware для проверки read-only
@app.middleware("http")
async def check_read_only(request, call_next):
    if os.getenv("READ_ONLY", "false").lower() == "true":
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Write operation not allowed on read-only replica",
                    "instance": os.getenv("APP_INSTANCE", "unknown")
                }
            )
    return await call_next(request)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Nady Bakery API",
        "instance": os.getenv("APP_INSTANCE", "unknown"),
        "db_role": os.getenv("DB_ROLE", "unknown"),
        "read_only": os.getenv("READ_ONLY", "false")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Nady Bakery API",
        "instance": os.getenv("APP_INSTANCE", "unknown")
    }

@app.get("/instance-info")
async def instance_info():
    return {
        "instance": os.getenv("APP_INSTANCE", "unknown"),
        "db_role": os.getenv("DB_ROLE", "unknown"),
        "read_only": os.getenv("READ_ONLY", "false")
    }

@app.post("/api/v2/test-write")
async def test_write():
    logger.info(f"Write test on instance: {os.getenv('APP_INSTANCE')}")
    return {
        "message": "Write test successful",
        "instance": os.getenv("APP_INSTANCE", "unknown")
    }

@app.get("/api/v2/data")
async def get_data():
    return {
        "data": "Sample data from bakery API",
        "instance": os.getenv("APP_INSTANCE", "unknown")
    }

@app.post("/api/v2/data")
async def create_data():
    return {
        "message": "Data created successfully",
        "instance": os.getenv("APP_INSTANCE", "unknown")
    }
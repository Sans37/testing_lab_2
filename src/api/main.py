# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v2.routers import api_router

# Создание приложения FastAPI
app = FastAPI(
    title="Nady Bakery API",
    description="API для системы онлайн-заказов пекарни Nady",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API v2
app.include_router(api_router, prefix="/api/v2")

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Nady Bakery API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Nady Bakery API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
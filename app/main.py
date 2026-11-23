from fastapi import FastAPI

from app.auth import router as auth_router
from app.pedidos import router as pedidos_router
from app.reportes import router as reportes_router
from app.reservas import router as reservas_router

app = FastAPI(
    title="Restaurante Sabor Andino",
    description="Gestión de reservas, pedidos en línea y reportes.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(reservas_router)
app.include_router(pedidos_router)
app.include_router(reportes_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "restaurante-sabor-andino"}

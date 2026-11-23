from fastapi import APIRouter, Depends

from app.auth import require_admin
from app.models import Reporte
from app.store import mesas, pedidos, reservas

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("", response_model=Reporte)
def obtener_reporte(_rol: str = Depends(require_admin)) -> Reporte:
    return Reporte(
        reservas_confirmadas=sum(1 for r in reservas.values() if r.estado == "confirmada"),
        pedidos_activos=sum(1 for p in pedidos.values() if p.estado not in {"entregado", "cancelado"}),
        mesas_disponibles=sum(1 for m in mesas if m.disponible),
    )

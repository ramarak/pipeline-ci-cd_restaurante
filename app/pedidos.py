from fastapi import APIRouter, HTTPException

from app.models import Pedido, PedidoCreate
from app.store import next_pedido_id, pedidos

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("", response_model=Pedido, status_code=201)
def crear_pedido(datos: PedidoCreate) -> Pedido:
    if not datos.items:
        raise HTTPException(status_code=400, detail="El pedido debe incluir al menos un plato")
    pedido = Pedido(
        id=next_pedido_id(),
        nombre_cliente=datos.nombre_cliente,
        items=datos.items,
        estado="recibido",
        total_items=sum(item.cantidad for item in datos.items),
    )
    pedidos[pedido.id] = pedido
    return pedido


@router.get("", response_model=list[Pedido])
def listar_pedidos() -> list[Pedido]:
    return list(pedidos.values())


@router.get("/{pedido_id}", response_model=Pedido)
def obtener_pedido(pedido_id: int) -> Pedido:
    pedido = pedidos.get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.patch("/{pedido_id}/estado", response_model=Pedido)
def actualizar_estado(pedido_id: int, estado: str) -> Pedido:
    permitidos = {"recibido", "en_preparacion", "listo", "entregado", "cancelado"}
    if estado not in permitidos:
        raise HTTPException(status_code=400, detail="Estado no válido")
    pedido = obtener_pedido(pedido_id)
    pedido.estado = estado
    return pedido

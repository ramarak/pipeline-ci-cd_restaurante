from app.models import Mesa, Pedido, Reserva

mesas: list[Mesa] = [
    Mesa(id=1, capacidad=2, disponible=True),
    Mesa(id=2, capacidad=4, disponible=True),
    Mesa(id=3, capacidad=6, disponible=True),
    Mesa(id=4, capacidad=8, disponible=True),
]

reservas: dict[int, Reserva] = {}
pedidos: dict[int, Pedido] = {}
_next_reserva = 1
_next_pedido = 1

USUARIOS = {
    "mesero": {"password": "mesero123", "rol": "mesero"},
    "admin": {"password": "admin123", "rol": "admin"},
}


def reset() -> None:
    global _next_reserva, _next_pedido
    reservas.clear()
    pedidos.clear()
    _next_reserva = 1
    _next_pedido = 1
    for mesa in mesas:
        mesa.disponible = True


def next_reserva_id() -> int:
    global _next_reserva
    value = _next_reserva
    _next_reserva += 1
    return value


def next_pedido_id() -> int:
    global _next_pedido
    value = _next_pedido
    _next_pedido += 1
    return value

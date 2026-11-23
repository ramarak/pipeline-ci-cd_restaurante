from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    usuario: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    rol: str


class Mesa(BaseModel):
    id: int
    capacidad: int
    disponible: bool = True


class ReservaCreate(BaseModel):
    mesa_id: int
    nombre_cliente: str = Field(min_length=2)
    personas: int = Field(ge=1, le=12)
    hora: str = Field(description="Formato HH:MM, horario 12:00-22:00")


class Reserva(ReservaCreate):
    id: int
    estado: str = "confirmada"


class PedidoItem(BaseModel):
    plato: str
    cantidad: int = Field(ge=1)


class PedidoCreate(BaseModel):
    nombre_cliente: str = Field(min_length=2)
    items: list[PedidoItem]


class Pedido(PedidoCreate):
    id: int
    estado: str = "recibido"
    total_items: int = 0


class Reporte(BaseModel):
    reservas_confirmadas: int
    pedidos_activos: int
    mesas_disponibles: int

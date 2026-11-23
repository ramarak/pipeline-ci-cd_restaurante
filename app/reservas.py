from fastapi import APIRouter, HTTPException

from app.models import Mesa, Reserva, ReservaCreate
from app.store import mesas, next_reserva_id, reservas

router = APIRouter(prefix="/reservas", tags=["reservas"])

HORA_MIN = 12
HORA_MAX = 22


def validar_hora(hora: str) -> None:
    partes = hora.split(":")
    if len(partes) != 2 or not all(p.isdigit() for p in partes):
        raise HTTPException(status_code=400, detail="Hora inválida. Use HH:MM")
    horas, minutos = int(partes[0]), int(partes[1])
    if minutos not in (0, 30) or not (HORA_MIN <= horas < HORA_MAX or (horas == HORA_MAX and minutos == 0)):
        raise HTTPException(
            status_code=400,
            detail="Horario de reservas: 12:00 a 22:00 en intervalos de 30 minutos",
        )


def obtener_mesa(mesa_id: int) -> Mesa:
    for mesa in mesas:
        if mesa.id == mesa_id:
            return mesa
    raise HTTPException(status_code=404, detail="Mesa no encontrada")


@router.get("/mesas", response_model=list[Mesa])
def listar_mesas() -> list[Mesa]:
    return mesas


@router.post("", response_model=Reserva, status_code=201)
def crear_reserva(datos: ReservaCreate) -> Reserva:
    validar_hora(datos.hora)
    mesa = obtener_mesa(datos.mesa_id)
    if not mesa.disponible:
        raise HTTPException(status_code=409, detail="La mesa no está disponible")
    if datos.personas > mesa.capacidad:
        raise HTTPException(status_code=400, detail="Capacidad de mesa insuficiente")
    mesa.disponible = False
    reserva = Reserva(id=next_reserva_id(), estado="confirmada", **datos.model_dump())
    reservas[reserva.id] = reserva
    return reserva


@router.get("", response_model=list[Reserva])
def listar_reservas() -> list[Reserva]:
    return list(reservas.values())


@router.delete("/{reserva_id}", response_model=Reserva)
def cancelar_reserva(reserva_id: int) -> Reserva:
    reserva = reservas.get(reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.estado = "cancelada"
    obtener_mesa(reserva.mesa_id).disponible = True
    return reserva

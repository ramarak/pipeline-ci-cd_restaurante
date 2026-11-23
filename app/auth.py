from fastapi import APIRouter, Depends, Header, HTTPException

from app.models import LoginRequest, TokenResponse
from app.store import USUARIOS

router = APIRouter(prefix="/auth", tags=["autenticacion"])

TOKENS = {
    "token-mesero": "mesero",
    "token-admin": "admin",
}


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest) -> TokenResponse:
    usuario = USUARIOS.get(datos.usuario)
    if not usuario or usuario["password"] != datos.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return TokenResponse(access_token=f"token-{datos.usuario}", rol=usuario["rol"])


def require_user(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.removeprefix("Bearer ").strip()
    rol = TOKENS.get(token)
    if not rol:
        raise HTTPException(status_code=401, detail="Token inválido")
    return rol


def require_admin(rol: str = Depends(require_user)) -> str:
    if rol != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return rol

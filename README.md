# Restaurante Sabor Andino — pipeline CI/CD

Sistema mínimo de reservas, pedidos, autenticación y reportes, con pipeline de integración y entrega continua.

## Requisitos

- Python 3.12
- Docker Desktop (opcional, para empaquetado y staging)

## Arranque local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/health  

Usuarios de demostración: `admin` / `admin123`, `mesero` / `mesero123`.

## Pipeline local (equivalente a GitHub Actions)

```powershell
ruff check .
pytest -v
bandit -r app -q
pip-audit -r requirements.txt
docker compose up --build -d
```

## Staging

```powershell
docker compose up --build -d
```

El informe académico está en `Informe_Pipeline_CI_CD_Restaurante.docx`.
Las evidencias visuales están en la carpeta `capturas/`.
Repositorio: https://github.com/ramarak/pipeline-ci-cd_restaurante

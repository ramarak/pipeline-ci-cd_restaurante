"""Ejecuta el flujo CI local y genera las PNG de evidencias en capturas/."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from render_terminal import render_code, render_terminal

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "capturas"
PY = ROOT / ".venv" / "Scripts" / "python.exe"
ENV = os.environ.copy()
ENV["PYTHONIOENCODING"] = "utf-8"
ENV["PYTHONPATH"] = str(ROOT)


def run(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENV,
    )
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    return proc.returncode, out.strip()


def py_mod(*mod_args: str) -> list[str]:
    return [str(PY), "-m", *mod_args]


def render_diagrama() -> None:
    from PIL import Image, ImageDraw, ImageFont

    dest = CAP / "captura-D-diagrama.png"
    img = Image.new("RGB", (1200, 520), (248, 248, 248))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
        font_b = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
        font_s = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 13)
    except OSError:
        font = font_b = font_s = ImageFont.load_default()
    draw.text((40, 18), "Pipeline CI/CD — Restaurante Sabor Andino", fill=(31, 78, 121), font=font_b)
    boxes = [
        (40, 120, "1. Lint\nRuff"),
        (250, 120, "2. Tests\npytest"),
        (460, 120, "3. Seguridad\nBandit + audit"),
        (690, 120, "4. Build\nDocker"),
        (920, 120, "5. Staging\nCompose"),
    ]
    for i, (x, y, label) in enumerate(boxes):
        draw.rounded_rectangle((x, y, x + 180, y + 90), radius=10, fill=(31, 78, 121), outline=(20, 50, 80))
        draw.text((x + 16, y + 24), label, fill=(255, 255, 255), font=font)
        if i < len(boxes) - 1:
            draw.polygon([(x + 188, y + 40), (x + 208, y + 50), (x + 188, y + 60)], fill=(31, 78, 121))
    draw.rounded_rectangle((250, 280, 430, 360), radius=10, fill=(168, 50, 50))
    draw.text((270, 304), "PIPELINE\nDETENIDO", fill=(255, 255, 255), font=font)
    draw.line((340, 210, 340, 280), fill=(168, 50, 50), width=3)
    draw.text((360, 240), "falla lint / test / seguridad", fill=(168, 50, 50), font=font_s)
    draw.rounded_rectangle((920, 280, 1160, 360), radius=10, outline=(31, 78, 121), width=2)
    draw.text((940, 300), "Producción\n(manual / tag)", fill=(31, 78, 121), font=font)
    draw.line((1010, 210, 1010, 280), fill=(31, 78, 121), width=3)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)
    print(f"OK {dest}")


def main() -> None:
    CAP.mkdir(parents=True, exist_ok=True)
    render_diagrama()

    tree_cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-ChildItem -Name | Where-Object { $_ -notin '.venv','.pytest_cache','.ruff_cache' }",
    ]
    code, out = run(tree_cmd)
    git_code, git_out = run(["git", "status"])
    render_terminal(
        "Repositorio — git status y estructura",
        "PS> Get-ChildItem; git status",
        out + "\n\n" + git_out,
        CAP / "captura-01-repositorio.png",
    )

    yaml_path = ROOT / ".github" / "workflows" / "ci-cd.yml"
    render_code("Editor — .github/workflows/ci-cd.yml", yaml_path.read_text(encoding="utf-8"), CAP / "captura-1b-yaml.png")
    docker_txt = (ROOT / "Dockerfile").read_text(encoding="utf-8") + "\n\n--- docker-compose.yml ---\n\n"
    docker_txt += (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    render_code("Empaquetado — Dockerfile y docker-compose.yml", docker_txt, CAP / "captura-08-staging-config.png")

    code, out = run(py_mod("ruff", "check", "."))
    render_terminal("Etapa lint — Ruff", "PS> python -m ruff check .", out or "All checks passed!", CAP / "captura-03-ruff.png")

    code, out = run(py_mod("pytest", "-v", "--tb=short"))
    render_terminal("Etapa pruebas — pytest (éxito)", "PS> python -m pytest -v", out, CAP / "captura-04-pytest-ok.png")
    render_terminal("Pruebas recuperadas", "PS> python -m pytest -v", out, CAP / "captura-06-pytest-correccion.png")

    test_file = ROOT / "tests" / "test_reservas.py"
    original = test_file.read_text(encoding="utf-8")
    broken = original.replace(
        '            "hora": "23:30",\n        },\n    )\n    assert respuesta.status_code == 400',
        '            "hora": "23:30",\n        },\n    )\n    assert respuesta.status_code == 201',
        1,
    )
    test_file.write_text(broken, encoding="utf-8")
    try:
        _code, out = run(py_mod("pytest", "-v", "--tb=short", "tests/test_reservas.py::test_reserva_hora_invalida"))
        render_terminal(
            "Fallo simulado — pytest en rojo",
            "PS> python -m pytest -v tests/test_reservas.py::test_reserva_hora_invalida",
            out,
            CAP / "captura-05-pytest-fallo.png",
            error=True,
        )
    finally:
        test_file.write_text(original, encoding="utf-8")

    _c1, bandit_out = run(py_mod("bandit", "-r", "app", "-c", ".bandit"))
    _c2, audit_out = run(py_mod("pip_audit", "-r", "requirements.txt"))
    render_terminal(
        "Seguridad — Bandit y pip-audit",
        "PS> python -m bandit -r app -c .bandit; python -m pip_audit -r requirements.txt",
        bandit_out + "\n\n" + audit_out,
        CAP / "captura-07-seguridad.png",
    )

    server = subprocess.Popen(
        [str(PY), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT),
        env=ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1)
                break
            except Exception:
                time.sleep(0.25)
        else:
            raise RuntimeError("Uvicorn no respondió en /health")

        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8000/docs", wait_until="networkidle")
            page.screenshot(path=str(CAP / "captura-02-api-docs.png"), full_page=True)
            page.goto("http://127.0.0.1:8000/health", wait_until="networkidle")
            page.screenshot(path=str(CAP / "captura-08-staging-health.png"))
            page.goto("http://127.0.0.1:8000/reservas/mesas", wait_until="networkidle")
            page.screenshot(path=str(CAP / "captura-02b-mesas.png"))
            browser.close()
        print("OK capturas de API con Playwright")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    print("Capturas locales listas en", CAP)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()

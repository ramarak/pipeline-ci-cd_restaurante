"""Genera el informe académico .docx del proyecto integrador CI/CD."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Informe_Pipeline_CI_CD_Restaurante.docx"
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"


def set_run_font(run, name="Calibri", size=12, bold=False, color=None, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


def shade_cell(cell, hex_color: str) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def add_paragraph(doc, text, *, size=12, bold=False, italic=False, align="left", space_after=8, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "justify":
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    return h


def resolve_captura(numero: str, archivo: str) -> Path | None:
    hinted = ROOT / archivo
    if hinted.exists() and hinted.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        return hinted
    folder = ROOT / "capturas"
    if not folder.exists():
        return None
    numero_l = numero.lower()
    candidates = {f"captura-{numero_l}"}
    if numero.isdigit():
        candidates.add(f"captura-{numero.zfill(2)}")
    for path in sorted(folder.glob("*.png")):
        stem = path.stem.lower()
        if any(stem == c or stem.startswith(c + "-") for c in candidates):
            return path
    return None


def add_captura(doc, numero: str, titulo: str, que: str, comando: str, archivo: str) -> None:
    img = resolve_captura(numero, archivo)
    add_paragraph(doc, f"Figura {numero}. {titulo}", size=11, italic=True, space_after=4)
    if img is not None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(img), width=Inches(6.1))
        add_paragraph(doc, f"Archivo: {img.as_posix()}", size=9, italic=True, space_after=10)
        return
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    shade_cell(cell, "D9D9D9")
    p0 = cell.paragraphs[0]
    r0 = p0.add_run(f"[CAPTURA {numero} — {titulo}]")
    set_run_font(r0, size=12, bold=True, color=RGBColor(0xC0, 0x00, 0x00))
    for etiqueta, valor in (
        ("Qué fotografiar", que),
        ("Comando o pantalla", comando),
        ("Archivo sugerido", archivo),
        ("Pendiente", "Aún no hay PNG en capturas/ para este recuadro."),
    ):
        p = cell.add_paragraph()
        r = p.add_run(f"{etiqueta}: ")
        set_run_font(r, size=11, bold=True)
        r2 = p.add_run(valor)
        set_run_font(r2, size=11)
    doc.add_paragraph()


def sanitize_xml(text: str) -> str:
    cleaned = "".join(ch if (ch in "\n\t" or ord(ch) >= 32) else " " for ch in text)
    return cleaned.replace("\x00", "")


def add_code_block(doc, text: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    shade_cell(cell, "F2F2F2")
    for i, line in enumerate(sanitize_xml(text).splitlines() or [""]):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run(line if line else " ")
        set_run_font(run, name="Consolas", size=9)
    doc.add_paragraph()


def build() -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # --- Portada ---
    for _ in range(3):
        add_paragraph(doc, "")
    add_paragraph(
        doc,
        "PROYECTO INTEGRADOR",
        size=14,
        bold=True,
        align="center",
        space_after=4,
    )
    add_paragraph(
        doc,
        "Construcción de un Pipeline CI/CD para un Sistema de Gestión de Pedidos y Reservas de Restaurante",
        size=18,
        bold=True,
        align="center",
        space_after=18,
    )
    add_paragraph(
        doc,
        "Sistema: Restaurante Sabor Andino",
        size=14,
        align="center",
        space_after=24,
    )
    add_paragraph(doc, "[Nombre completo del estudiante]", size=13, align="center", space_after=6)
    add_paragraph(doc, "[Nombre del curso]", size=13, align="center", space_after=6)
    add_paragraph(doc, "[Fecha de entrega]", size=13, align="center", space_after=6)
    add_paragraph(
        doc,
        "Gestión del software — ABP: Pipeline de integración y entrega continua",
        size=11,
        italic=True,
        align="center",
        space_after=12,
    )
    doc.add_page_break()

    # --- Introducción ---
    add_heading_custom(doc, "1. Introducción", 1)
    add_heading_custom(doc, "1.1 Contexto del sistema de restaurante", 2)
    add_paragraph(
        doc,
        "Restaurante Sabor Andino es un sistema de software orientado a la operación diaria de un restaurante: "
        "los comensales consultan la disponibilidad de mesas, realizan reservas en un horario definido y envían "
        "pedidos en línea; el personal confirma estados y el administrador consulta reportes de ocupación. "
        "En este proyecto se implementó una API REST con FastAPI que cubre esos módulos de forma mínima pero ejecutable, "
        "con datos en memoria, para demostrar el ciclo de vida de integración, prueba y despliegue sin depender de una base de datos externa.",
        align="justify",
    )
    add_paragraph(
        doc,
        "El escenario es realista: un error en la regla de horario de reservas o un despliegue manual mal ejecutado "
        "puede dejar mesas doblemente asignadas o un servicio caído en hora pico. Por eso el valor del trabajo no está "
        "solo en las funcionalidades, sino en automatizar la calidad antes de que el cambio llegue a un entorno de pruebas.",
        align="justify",
    )

    add_heading_custom(doc, "1.2 Justificación de un pipeline automatizado", 2)
    add_paragraph(
        doc,
        "Sin un pipeline, cada integrante del equipo compila, prueba y publica de manera distinta. Eso introduce errores "
        "humanos, retrasa las entregas y dificulta detectar regresiones. Un pipeline de integración y entrega continua (CI/CD) "
        "estandariza el flujo: cada push o pull request dispara análisis estático, pruebas, revisión de seguridad, "
        "empaquetado en contenedor y un despliegue controlado a staging. El objetivo es entregas frecuentes, repetibles y "
        "con evidencia de calidad, alineadas con las prácticas DevOps y de aseguramiento de calidad del curso.",
        align="justify",
    )

    # --- Desarrollo: análisis ---
    add_heading_custom(doc, "2. Desarrollo", 1)
    add_heading_custom(doc, "2.1 Análisis del sistema", 2)
    add_heading_custom(doc, "2.1.1 Funcionalidades principales", 3)
    add_paragraph(
        doc,
        "El sistema expone los siguientes casos de uso, cubiertos por la API y por pruebas automatizadas:",
        align="justify",
    )
    bullets = [
        "Autenticación de usuarios de demostración (roles mesero y administrador) mediante token Bearer.",
        "Consulta de mesas y de su disponibilidad.",
        "Creación de reservas con validación de horario (12:00 a 22:00, intervalos de 30 minutos) y de capacidad.",
        "Cancelación de reservas, que libera la mesa.",
        "Pedidos en línea con ítems, consulta de estado y transición (recibido, en preparación, listo, entregado o cancelado).",
        "Reportes de reservas confirmadas, pedidos activos y mesas disponibles (solo rol admin).",
        "Endpoint de salud (/health) para monitoreo y para el healthcheck del contenedor.",
    ]
    for b in bullets:
        doc.add_paragraph(b, style="List Bullet")

    add_heading_custom(doc, "2.1.2 Módulos incluidos en el pipeline", 3)
    add_paragraph(
        doc,
        "Todos los módulos de aplicación se construyen, analizan y prueban en el mismo pipeline, porque un fallo en cualquiera "
        "de ellos puede romper el servicio desplegado:",
        align="justify",
    )

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, t in enumerate(("Módulo", "Ruta en el código", "Por qué entra al pipeline")):
        hdr[i].text = t
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
        shade_cell(hdr[i], "1F4E79")
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(255, 255, 255)
    rows = [
        ("Autenticación", "app/auth.py", "Protege reportes y evita regresiones de autorización."),
        ("Reservas y mesas", "app/reservas.py", "Reglas de negocio críticas (horario, capacidad, disponibilidad)."),
        ("Pedidos", "app/pedidos.py", "Flujo de pedidos en línea y cambios de estado."),
        ("Reportes", "app/reportes.py", "Indicadores operativos; requiere rol admin."),
        ("API y salud", "app/main.py", "Punto de entrada y contrato /health para despliegue."),
        ("Pruebas", "tests/", "Suite pytest que el job de CI debe pasar obligatoriamente."),
        ("Empaquetado", "Dockerfile y docker-compose.yml", "Imagen y entorno staging simulados."),
        ("Orquestación", ".github/workflows/ci-cd.yml", "Definición de etapas, dependencias y fail-fast."),
    ]
    for fila in rows:
        cells = table.add_row().cells
        for i, val in enumerate(fila):
            cells[i].text = val
    doc.add_paragraph()

    add_heading_custom(doc, "2.1.3 Puntos críticos del flujo de desarrollo a automatizar", 3)
    criticos = [
        "Integración del código: cada cambio se valida igual, sin pasos manuales olvidados.",
        "Calidad de código: el linter (Ruff) detiene el pipeline si hay errores de estilo o imports rotos.",
        "Pruebas automatizadas: pytest cubre reservas inválidas, pedidos vacíos y acceso denegado a reportes.",
        "Seguridad: Bandit (análisis estático) y pip-audit (vulnerabilidades en dependencias).",
        "Empaquetado reproducible: imagen Docker con la misma receta en CI y en staging.",
        "Despliegue a un entorno de pruebas (staging) solo si las etapas previas fueron exitosas.",
        "Fail-fast: un fallo en lint, test o seguridad impide construir y desplegar.",
    ]
    for b in criticos:
        doc.add_paragraph(b, style="List Bullet")

    add_captura(
        doc,
        "1",
        "Repositorio y control de versiones",
        "Estructura del proyecto (carpetas app, tests, .github) o la salida de git status / git log.",
        "Explorador de archivos del proyecto, o en PowerShell: git status",
        "capturas/captura-1.png",
    )

    # --- Diseño ---
    add_heading_custom(doc, "2.2 Diseño del pipeline CI/CD", 2)
    add_heading_custom(doc, "2.2.1 Etapas principales", 3)
    add_paragraph(
        doc,
        "El pipeline se dispara en push y en pull request. Las etapas son secuenciales: cada job declara needs respecto del anterior, "
        "de modo que no se invierte tiempo en construir una imagen si las pruebas ya fallaron.",
        align="justify",
    )
    etapas = [
        "Calidad (lint): Ruff analiza el código fuente.",
        "Pruebas: se instalan dependencias de desarrollo y se ejecuta pytest -v.",
        "Seguridad: Bandit sobre app/ y pip-audit sobre requirements.txt.",
        "Construcción: docker build genera la imagen etiquetada con el SHA del commit.",
        "Despliegue a staging: en la rama principal se valida docker compose (simulación de publicación al entorno de pruebas). "
        "La promoción a producción no es automática: queda como puerta posterior (tag o aprobación).",
    ]
    for b in etapas:
        doc.add_paragraph(b, style="List Number")

    add_heading_custom(doc, "2.2.2 Herramientas por etapa", 3)
    tools = doc.add_table(rows=1, cols=3)
    tools.style = "Table Grid"
    for i, t in enumerate(("Etapa", "Herramienta", "Rol")):
        tools.rows[0].cells[i].text = t
        shade_cell(tools.rows[0].cells[i], "1F4E79")
        for p in tools.rows[0].cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
    for fila in [
        ("Control de versiones", "Git", "Historial, ramas y disparador del pipeline."),
        ("Orquestación", "GitHub Actions", "Jobs, artefactos lógicos y condiciones por rama."),
        ("Calidad de código", "Ruff", "Análisis estático rápido (PEP8, errores)."),
        ("Pruebas", "pytest + TestClient de FastAPI", "Pruebas unitarias y de API sin servidor externo."),
        ("Seguridad", "Bandit y pip-audit", "SAST y vulnerabilidades de paquetes."),
        ("Empaquetado", "Docker", "Imagen inmutable del servicio."),
        ("Staging", "Docker Compose", "Servicio con healthcheck en puerto 8000."),
        ("Rendimiento / disponibilidad", "scripts/carga_salud.py y HEALTHCHECK", "Latencia de /health y reinicio si el contenedor enferma."),
        ("API de demostración", "FastAPI + Uvicorn", "Contrato REST y documentación /docs."),
    ]:
        cells = tools.add_row().cells
        for i, val in enumerate(fila):
            cells[i].text = val
    doc.add_paragraph()

    add_heading_custom(doc, "2.2.3 Diagrama del pipeline", 3)
    add_paragraph(
        doc,
        "La secuencia automatizada es la siguiente. Cualquier X en lint, pruebas o seguridad detiene el flujo (no hay build ni deploy).",
        align="justify",
    )
    add_code_block(
        doc,
        "Push / Pull Request\n"
        "        |\n"
        "        v\n"
        "   [1. Lint — Ruff] ----falla---> PIPELINE DETENIDO\n"
        "        | ok\n"
        "        v\n"
        "   [2. Pruebas — pytest] ----falla---> PIPELINE DETENIDO\n"
        "        | ok\n"
        "        v\n"
        "   [3. Seguridad — Bandit + pip-audit] ----falla---> PIPELINE DETENIDO\n"
        "        | ok\n"
        "        v\n"
        "   [4. Build — imagen Docker]\n"
        "        |\n"
        "        v\n"
        "   [5. Deploy staging — Compose]  (solo rama main/master)\n"
        "        |\n"
        "        v\n"
        "   [Puerta a producción]  (manual / tag / aprobación — no automática)",
    )
    add_captura(
        doc,
        "D",
        "Diagrama propio (opcional)",
        "Si exporta el diagrama (por ejemplo desde draw.io, Lucidchart o Mermaid) como PNG, péguelo aquí. "
        "Si no, el esquema de texto anterior es suficiente para el taller.",
        "Herramienta de diagramas → Exportar PNG",
        "capturas/captura-D-diagrama.png",
    )

    add_heading_custom(doc, "2.2.4 Archivo de configuración (GitHub Actions)", 3)
    add_paragraph(
        doc,
        "El orquestador real del proyecto es el flujo YAML versionado en .github/workflows/ci-cd.yml. "
        "A continuación se cita el archivo utilizado (no es un pseudocódigo genérico: corresponde al repositorio de este ABP).",
        align="justify",
    )
    yaml_text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else "(archivo no encontrado)"
    add_code_block(doc, yaml_text)

    add_captura(
        doc,
        "1b",
        "Workflow YAML en el editor",
        "Archivo .github/workflows/ci-cd.yml abierto en el editor, para evidenciar que la configuración existe en el repo.",
        "Abrir .github/workflows/ci-cd.yml",
        "capturas/captura-1b-yaml.png",
    )
    add_captura(
        doc,
        "2",
        "API en ejecución",
        "Servidor Uvicorn en la terminal y, al lado, el navegador en la documentación Swagger o una respuesta JSON de mesas/health.",
        "uvicorn app.main:app --reload   y   http://127.0.0.1:8000/docs",
        "capturas/captura-2.png",
    )

    # --- Simulación ---
    add_heading_custom(doc, "2.3 Simulación de ejecución del pipeline", 2)
    add_heading_custom(doc, "2.3.1 Cómo se simula (y se ejecuta de verdad en local)", 3)
    add_paragraph(
        doc,
        "GitHub Actions ejecutará el YAML cuando el repositorio se publique en GitHub. Mientras tanto, el mismo orden de etapas "
        "se corre en la máquina de desarrollo. Eso produce evidencias reales de consola, que el taller acepta como simulación o ejecución. "
        "Pasos:",
        align="justify",
    )
    pasos = [
        "Instalar dependencias: pip install -r requirements-dev.txt",
        "Etapa lint: ruff check .  → se espera exit code 0.",
        "Etapa pruebas: pytest -v  → todos los tests en PASSED.",
        "Etapa seguridad: bandit -r app -c .bandit y pip-audit -r requirements.txt.",
        "Etapa build/deploy: docker build y/o docker compose up --build -d, luego consultar /health.",
        "Simulación de fallo: alterar una aserción, volver a correr pytest, capturar el rojo, revertir y repetir en verde.",
    ]
    for b in pasos:
        doc.add_paragraph(b, style="List Number")

    add_heading_custom(doc, "2.3.2 Resultados esperados por etapa", 3)
    esperados = doc.add_table(rows=1, cols=3)
    esperados.style = "Table Grid"
    for i, t in enumerate(("Etapa", "Resultado esperado", "Si falla")):
        esperados.rows[0].cells[i].text = t
        shade_cell(esperados.rows[0].cells[i], "1F4E79")
        for p in esperados.rows[0].cells[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
    for fila in [
        ("Lint", "All checks passed. Sin errores E/F/I/W.", "No se ejecutan tests. El autor corrige estilo o imports."),
        ("Pruebas", "N tests passed (reservas, pedidos, auth, reportes, health).", "No hay seguridad ni imagen. Se corrige la regla de negocio o el test."),
        ("Seguridad", "Bandit sin hallazgos de severidad configurada; pip-audit sin CVE conocidas en requirements.txt.", "Se actualiza el paquete o se justifica/mitiga el hallazgo."),
        ("Build", "Imagen Docker construida con tag del commit.", "Revisar Dockerfile y dependencias de runtime."),
        ("Staging", "Contenedor healthy; GET /health responde {\"status\":\"ok\"}.", "Revisar logs del contenedor y el healthcheck."),
        ("Producción (no auto)", "Solo tras aprobación o tag, fuera de este laboratorio.", "No se publica si staging no está estable."),
    ]:
        cells = esperados.add_row().cells
        for i, val in enumerate(fila):
            cells[i].text = val
    doc.add_paragraph()

    add_heading_custom(doc, "2.3.3 Evidencias de ejecución exitosa", 3)
    add_paragraph(
        doc,
        "Los archivos de texto en la carpeta evidencias/ reproducen la salida de consola obtenida al correr el pipeline local. "
        "Pegue además las capturas indicadas (la rúbrica pide pantallazos).",
        align="justify",
    )
    add_captura(
        doc,
        "3",
        "Lint en verde",
        "Salida de Ruff sin errores (All checks passed).",
        "ruff check .",
        "capturas/captura-3.png",
    )
    add_captura(
        doc,
        "4",
        "Pruebas unitarias exitosas",
        "pytest en modo verbose con todos los casos PASSED (incluido test_reserva_hora_invalida).",
        "pytest -v",
        "capturas/captura-4.png",
    )

    lint_log = ROOT / "evidencias" / "01_ruff.txt"
    test_log = ROOT / "evidencias" / "02_pytest_ok.txt"
    if lint_log.exists():
        add_paragraph(doc, "Salida registrada de Ruff:", italic=True)
        add_code_block(doc, lint_log.read_text(encoding="utf-8", errors="replace")[:2500])
    if test_log.exists():
        add_paragraph(doc, "Salida registrada de pytest (éxito):", italic=True)
        add_code_block(doc, test_log.read_text(encoding="utf-8", errors="replace")[:3500])

    add_heading_custom(doc, "2.3.4 Simulación de fallo y medidas de corrección", 3)
    add_paragraph(
        doc,
        "Para demostrar el fail-fast se provocó un fallo en la etapa de pruebas: se cambió temporalmente la aserción de "
        "test_reserva_hora_invalida para esperar código 201 (éxito) cuando una reserva a las 23:30 debe responder 400. "
        "pytest falló, el pipeline local se detuvo y no tendría sentido construir la imagen ni desplegar. "
        "La corrección consistió en restaurar la aserción correcta (status_code == 400) y volver a ejecutar la suite.",
        align="justify",
    )
    add_paragraph(
        doc,
        "Medidas de corrección aplicables en un equipo real: leer el nombre del test y el traceback, reproducir el caso "
        "(hora fuera de rango), ajustar la regla de negocio o el test, no desactivar la etapa, y solo entonces repetir CI. "
        "En GitHub, el check del pull request permanecería en rojo y bloquearía el merge si se configura branch protection.",
        align="justify",
    )
    add_captura(
        doc,
        "5",
        "Pruebas fallidas (simulación)",
        "pytest en rojo: al menos un FAILED (por ejemplo test_reserva_hora_invalida). Debe verse el traceback.",
        "Altere por un momento tests/test_reservas.py (espere 201 en hora inválida) y ejecute: pytest -v",
        "capturas/captura-5.png",
    )
    fail_log = ROOT / "evidencias" / "03_pytest_fallo.txt"
    if fail_log.exists():
        add_paragraph(doc, "Salida registrada del fallo simulado:", italic=True)
        add_code_block(doc, fail_log.read_text(encoding="utf-8", errors="replace")[:3500])

    add_captura(
        doc,
        "6",
        "Pruebas recuperadas tras la corrección",
        "Misma suite pytest otra vez en verde, después de devolver la aserción a 400.",
        "pytest -v",
        "capturas/captura-6.png",
    )

    add_heading_custom(doc, "2.3.5 Empaquetado y staging", 3)
    add_paragraph(
        doc,
        "El Dockerfile instala requirements.txt, copia app/ y arranca Uvicorn en el puerto 8000, con HEALTHCHECK sobre /health. "
        "docker-compose.yml publica el servicio staging. Si Docker Desktop no está disponible en el momento de la captura, "
        "se adjunta el comando esperado y se deja el recuadro para cuando sí lo esté.",
        align="justify",
    )
    add_captura(
        doc,
        "8",
        "Docker / despliegue a staging",
        "Construcción de la imagen o contenedor en ejecución, más una consulta a /health (navegador, curl o Invoke-WebRequest).",
        "docker compose up --build -d     y     http://127.0.0.1:8000/health",
        "capturas/captura-8.png",
    )
    add_captura(
        doc,
        "9",
        "GitHub Actions en verde (opcional)",
        "Pestaña Actions del repositorio con el workflow CI/CD Restaurante Sabor Andino exitoso. Solo aplica si sube el proyecto a GitHub.",
        "GitHub → repositorio → Actions → último run",
        "capturas/captura-9.png",
    )
    add_captura(
        doc,
        "10",
        "GitHub Actions en rojo (opcional)",
        "Un run fallido del mismo workflow (por ejemplo el commit con el test roto), para contrastar con la captura 9.",
        "GitHub → Actions → run failed",
        "capturas/captura-10.png",
    )

    # --- NFR ---
    add_heading_custom(doc, "2.4 Validación de calidad y seguridad (requisitos no funcionales)", 2)
    add_paragraph(
        doc,
        "El pipeline no solo verifica que “la reserva se cree”. También incorpora controles de requisitos no funcionales, "
        "aunque en este laboratorio se aplican de forma proporcional al tamaño del sistema.",
        align="justify",
    )
    add_heading_custom(doc, "2.4.1 Seguridad", 3)
    add_paragraph(
        doc,
        "Técnica 1 — análisis estático de seguridad (SAST) con Bandit: recorre app/ en busca de patrones inseguros "
        "(por ejemplo ejecución de shell, uso inseguro de pickle o secretos embebidos). En este proyecto las credenciales "
        "de demostración viven en app/store.py a propósito del laboratorio; en producción irían a secretos del orquestador "
        "(GitHub Secrets) y Bandit no se saltaría esa regla. El archivo .bandit documenta el skip B105 solo para el demo.",
        align="justify",
    )
    add_paragraph(
        doc,
        "Técnica 2 — escaneo de vulnerabilidades de dependencias con pip-audit: compara requirements.txt con bases de CVE. "
        "Si aparece una librería vulnerable, el job security falla y no se construye la imagen. Complemento de runtime: "
        "los reportes exigen token y rol admin (pruebas de autorización en tests/test_auth.py y tests/test_reportes.py).",
        align="justify",
    )
    add_captura(
        doc,
        "7",
        "Seguridad (Bandit y/o pip-audit)",
        "Resumen de Bandit (No issues identified, o listado de hallazgos) y, si es posible en la misma captura o en una segunda, pip-audit.",
        "bandit -r app -c .bandit     y     pip-audit -r requirements.txt",
        "capturas/captura-7.png",
    )
    bandit_log = ROOT / "evidencias" / "04_bandit.txt"
    audit_log = ROOT / "evidencias" / "05_pip_audit.txt"
    if bandit_log.exists():
        add_paragraph(doc, "Salida registrada de Bandit:", italic=True)
        add_code_block(doc, bandit_log.read_text(encoding="utf-8", errors="replace")[:2500])
    if audit_log.exists():
        add_paragraph(doc, "Salida registrada de pip-audit:", italic=True)
        add_code_block(doc, audit_log.read_text(encoding="utf-8", errors="replace")[:2500])

    add_heading_custom(doc, "2.4.2 Rendimiento", 3)
    add_paragraph(
        doc,
        "No se pretendió un test de estrés de producción (JMeter/k6 a miles de usuarios), pero sí una técnica integrable al pipeline: "
        "el script scripts/carga_salud.py dispara 20 solicitudes a /health, calcula latencia promedio y percentil 95, y falla si hay errores. "
        "Esa prueba se corre contra el servicio ya levantado (local o contenedor staging) y puede añadirse como job posterior al deploy. "
        "Sirve como humo de rendimiento: si /health se degrada, el entorno de pruebas no se considera listo.",
        align="justify",
    )
    add_heading_custom(doc, "2.4.3 Disponibilidad", 3)
    add_paragraph(
        doc,
        "Docker declara HEALTHCHECK periódico contra /health. Compose usa la misma sonda. Si el proceso no responde, el motor "
        "marca el contenedor como unhealthy, lo que en un orquestador (y en una extensión a Kubernetes) permitiría reinicio o "
        "corte de tráfico. En el laboratorio, un GET 200 a /health es la evidencia de que el servicio de staging está disponible.",
        align="justify",
    )

    # --- Buenas prácticas ---
    add_heading_custom(doc, "2.5 Buenas prácticas y automatización sugerida", 2)
    add_heading_custom(doc, "2.5.1 Prácticas implementadas en este pipeline", 3)
    practicas = [
        "Fail-fast: lint → test → security → build → deploy; un eslabón roto corta la cadena.",
        "Pruebas automatizadas obligatorias sobre reglas de negocio (horario, capacidad, autorización).",
        "Análisis estático de código y de seguridad en cada cambio, no “cuando haya tiempo”.",
        "Empaquetado inmutable (imagen Docker) en lugar de copiar archivos a mano al servidor.",
        "Entorno de staging separado de la idea de producción; producción no se publica en cada commit.",
        "Configuración del pipeline como código (YAML en Git), revisable en el mismo pull request que el feature.",
        "Usuarios de demo documentados; secretos reales no pertenecen al repositorio.",
        "Healthcheck como contrato de “el servicio vive”, útil para monitoreo posterior.",
    ]
    for b in practicas:
        doc.add_paragraph(b, style="List Bullet")

    add_paragraph(
        doc,
        "Revisión de código: aunque GitHub Actions no sustituye a una persona, el flujo está pensado para pull requests. "
        "La práctica recomendada es exigir al menos una aprobación y que los checks de CI estén en verde (branch protection) "
        "antes de fusionar a main.",
        align="justify",
    )

    add_heading_custom(doc, "2.5.2 Escalado a producción y trabajo colaborativo", 3)
    add_paragraph(
        doc,
        "Para pasar de este laboratorio a un equipo y a producción se sugieren estas estrategias:",
        align="justify",
    )
    escala = [
        "Ramas por historia (feature/*) + pull request obligatorio hacia main.",
        "GitHub Environments: staging automático; production con revisores y secretos distintos (URL, tokens, registry).",
        "Versionado de imágenes por tag semántico o SHA, almacenadas en un registry (GHCR o Docker Hub).",
        "Despliegue controlado: rolling update o blue-green; nunca “borrar y copiar” en el servidor de producción.",
        "Observabilidad: logs estructurados, métricas de latencia de /health y alertas si el healthcheck falla.",
        "Datos persistentes: migrar el almacén en memoria a PostgreSQL (u otro motor) con migraciones en el pipeline.",
        "Pruebas de carga más serias (k6 o Locust) en un job nightly, no necesariamente en cada commit.",
        "Infraestructura como código (Compose/Kubernetes manifests) revisada junto con la aplicación.",
    ]
    for b in escala:
        doc.add_paragraph(b, style="List Bullet")

    # --- Conclusiones ---
    add_heading_custom(doc, "3. Conclusiones", 1)
    add_heading_custom(doc, "3.1 Importancia de los pipelines en el desarrollo moderno", 2)
    add_paragraph(
        doc,
        "Un pipeline CI/CD convierte la calidad en un trámite automático e inevitable. En un restaurante digital, eso significa "
        "que una reserva mal validada no llega a staging, que una dependencia con CVE no se empaca “porque urge”, y que el "
        "despliegue deja de ser un ritual manual distinto en cada máquina. La integración continua reduce el costo de encontrar "
        "defectos; la entrega continua (aunque aquí se detenga en staging) acorta el tiempo entre la idea y un entorno verificable. "
        "Ese es el control de calidad que el taller pide demostrar: no un discurso, sino etapas que fallan en rojo cuando deben fallar.",
        align="justify",
    )
    add_heading_custom(doc, "3.2 Aprendizajes adquiridos", 2)
    aprendizajes = [
        "Diseñar el sistema en módulos (auth, reservas, pedidos, reportes) facilita probar y automatizar por contrato HTTP.",
        "El YAML de GitHub Actions es código de producto: se versiona, se revisa y debe coincidir con lo que se corre en local.",
        "Simular un fallo (test de horario) evidencia el valor del pipeline mejor que una corrida perfecta.",
        "Seguridad y rendimiento no son “fases finales”: Bandit, pip-audit y un smoke de /health caben en el mismo flujo.",
        "Staging con Docker es suficiente para un laboratorio académico y es un puente claro hacia producción con entornos y aprobaciones.",
        "Las evidencias (logs y capturas) son parte del aseguramiento de calidad: demuestran que el proceso ocurrió, no solo que se describió.",
    ]
    for b in aprendizajes:
        doc.add_paragraph(b, style="List Bullet")
    add_paragraph(
        doc,
        "En conjunto, el proyecto muestra un ciclo de vida de software en el que compilar, probar y desplegar deja de ser una "
        "secuencia artesanal y pasa a ser una cadena repetible, alineada con DevOps y con entregas frecuentes de calidad.",
        align="justify",
    )

    add_heading_custom(doc, "Referencias de trabajo (repositorio)", 2)
    add_paragraph(doc, "Código de aplicación: carpeta app/ (FastAPI).")
    add_paragraph(doc, "Pruebas: carpeta tests/.")
    add_paragraph(doc, "Pipeline: .github/workflows/ci-cd.yml")
    add_paragraph(doc, "Logs de consola: carpeta evidencias/")
    add_paragraph(doc, "Guía rápida de ejecución: README.md")

    doc.save(OUT)
    print(f"Generado: {OUT}")


if __name__ == "__main__":
    build()

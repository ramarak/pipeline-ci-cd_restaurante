"""Renderiza salida de consola real como captura PNG (ventana tipo PowerShell)."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ):
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render_terminal(title: str, prompt_line: str, body: str, dest: Path, *, error: bool = False) -> None:
    body = ANSI.sub("", body)
    body = CTRL.sub("", body)
    lines = (prompt_line + "\n" + body).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if len(lines) > 42:
        lines = lines[:42] + ["..."]
    font = _font(15)
    title_font = _font(13)
    pad_x, pad_y = 18, 52
    line_h = 20
    width = 1100
    height = pad_y + 16 + line_h * max(len(lines), 12) + 24
    img = Image.new("RGB", (width, height), (12, 12, 12))
    draw = ImageDraw.Draw(img)
    bar = (45, 45, 45) if not error else (92, 32, 32)
    draw.rectangle((0, 0, width, 36), fill=bar)
    draw.ellipse((14, 12, 26, 24), fill=(232, 81, 81))
    draw.ellipse((34, 12, 46, 24), fill=(230, 193, 70))
    draw.ellipse((54, 12, 66, 24), fill=(88, 184, 92))
    draw.text((84, 10), title, fill=(230, 230, 230), font=title_font)
    y = pad_y
    for i, line in enumerate(lines):
        if len(line) > 120:
            line = line[:117] + "..."
        if i == 0:
            color = (80, 200, 120)
        elif error and ("FAILED" in line or "Error" in line or "assert" in line):
            color = (255, 120, 120)
        elif "passed" in line.lower() or "All checks passed" in line or "No issues" in line or "No known" in line:
            color = (120, 220, 140)
        else:
            color = (220, 220, 220)
        draw.text((pad_x, y), line, fill=color, font=font)
        y += line_h
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG")
    print(f"OK {dest}")


def render_code(title: str, text: str, dest: Path) -> None:
    lines = text.replace("\r\n", "\n").split("\n")
    if len(lines) > 48:
        lines = lines[:48] + ["..."]
    font = _font(14)
    title_font = _font(13)
    pad_x, pad_y = 18, 52
    line_h = 18
    width = 1100
    height = pad_y + 12 + line_h * max(len(lines), 16) + 20
    img = Image.new("RGB", (width, height), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 36), fill=(50, 50, 50))
    draw.text((16, 10), title, fill=(230, 230, 230), font=title_font)
    y = pad_y
    for line in lines:
        if len(line) > 118:
            line = line[:115] + "..."
        draw.text((pad_x, y), line, fill=(210, 210, 210), font=font)
        y += line_h
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG")
    print(f"OK {dest}")

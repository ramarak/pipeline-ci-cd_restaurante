"""Prueba ligera de disponibilidad/rendimiento contra /health."""

import statistics
import time
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/health"
INTENTOS = 20


def main() -> None:
    latencias: list[float] = []
    errores = 0
    for _ in range(INTENTOS):
        inicio = time.perf_counter()
        try:
            with urllib.request.urlopen(URL, timeout=3) as respuesta:
                if respuesta.status != 200:
                    errores += 1
        except (urllib.error.URLError, TimeoutError):
            errores += 1
        latencias.append((time.perf_counter() - inicio) * 1000)
    ok = INTENTOS - errores
    print(f"Solicitudes: {INTENTOS}")
    print(f"Exitosas: {ok}")
    print(f"Errores: {errores}")
    print(f"Latencia promedio ms: {statistics.mean(latencias):.2f}")
    print(f"Latencia p95 ms: {sorted(latencias)[int(0.95 * (len(latencias) - 1))]:.2f}")
    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

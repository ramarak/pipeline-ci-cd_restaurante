def test_login_ok(client):
    respuesta = client.post("/auth/login", json={"usuario": "admin", "password": "admin123"})
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["rol"] == "admin"
    assert cuerpo["access_token"] == "token-admin"


def test_login_invalido(client):
    respuesta = client.post("/auth/login", json={"usuario": "admin", "password": "mala"})
    assert respuesta.status_code == 401


def test_reporte_sin_token(client):
    respuesta = client.get("/reportes")
    assert respuesta.status_code == 401

def test_listar_mesas(client):
    respuesta = client.get("/reservas/mesas")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 4


def test_crear_reserva_ok(client):
    respuesta = client.post(
        "/reservas",
        json={
            "mesa_id": 1,
            "nombre_cliente": "Ana Pérez",
            "personas": 2,
            "hora": "19:00",
        },
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "confirmada"
    mesas = client.get("/reservas/mesas").json()
    assert mesas[0]["disponible"] is False


def test_reserva_hora_invalida(client):
    respuesta = client.post(
        "/reservas",
        json={
            "mesa_id": 1,
            "nombre_cliente": "Ana Pérez",
            "personas": 2,
            "hora": "23:30",
        },
    )
    assert respuesta.status_code == 400


def test_reserva_capacidad_excedida(client):
    respuesta = client.post(
        "/reservas",
        json={
            "mesa_id": 1,
            "nombre_cliente": "Grupo grande",
            "personas": 10,
            "hora": "13:00",
        },
    )
    assert respuesta.status_code == 400


def test_cancelar_reserva(client):
    creada = client.post(
        "/reservas",
        json={
            "mesa_id": 2,
            "nombre_cliente": "Luis",
            "personas": 3,
            "hora": "20:00",
        },
    ).json()
    respuesta = client.delete(f"/reservas/{creada['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "cancelada"
    mesas = client.get("/reservas/mesas").json()
    assert mesas[1]["disponible"] is True

def test_reporte_admin(client, admin_headers):
    client.post(
        "/reservas",
        json={"mesa_id": 1, "nombre_cliente": "Ana", "personas": 2, "hora": "14:00"},
    )
    client.post(
        "/pedidos",
        json={"nombre_cliente": "Ana", "items": [{"plato": "Ajiaco", "cantidad": 1}]},
    )
    respuesta = client.get("/reportes", headers=admin_headers)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["reservas_confirmadas"] == 1
    assert cuerpo["pedidos_activos"] == 1
    assert cuerpo["mesas_disponibles"] == 3


def test_reporte_prohibido_mesero(client):
    respuesta = client.get("/reportes", headers={"Authorization": "Bearer token-mesero"})
    assert respuesta.status_code == 403

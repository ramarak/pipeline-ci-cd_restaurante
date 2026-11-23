def test_crear_y_consultar_pedido(client):
    respuesta = client.post(
        "/pedidos",
        json={
            "nombre_cliente": "Carla",
            "items": [{"plato": "Bandeja paisa", "cantidad": 2}, {"plato": "Jugo", "cantidad": 2}],
        },
    )
    assert respuesta.status_code == 201
    pedido_id = respuesta.json()["id"]
    assert respuesta.json()["total_items"] == 4

    consulta = client.get(f"/pedidos/{pedido_id}")
    assert consulta.status_code == 200
    assert consulta.json()["estado"] == "recibido"


def test_pedido_sin_items(client):
    respuesta = client.post("/pedidos", json={"nombre_cliente": "Carla", "items": []})
    assert respuesta.status_code == 400


def test_actualizar_estado(client):
    pedido = client.post(
        "/pedidos",
        json={"nombre_cliente": "Mario", "items": [{"plato": "Sopa", "cantidad": 1}]},
    ).json()
    respuesta = client.patch(f"/pedidos/{pedido['id']}/estado", params={"estado": "listo"})
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "listo"

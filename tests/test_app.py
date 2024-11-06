from http import HTTPStatus

from fastapi.testclient import TestClient

from pbl_redes_ii.server_a import server_a

client = TestClient(server_a)


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(server_a)

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Jesus é o único salvador"}

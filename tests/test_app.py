from http import HTTPStatus

from fastapi.testclient import TestClient

from pbl_redes_ii.app import app

client = TestClient(app)


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Jesus é o único salvador"}

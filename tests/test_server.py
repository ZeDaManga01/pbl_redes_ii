from fastapi.testclient import TestClient

from pbl_redes_ii_z.server_a import server_a

HTTP_OK = 200

client = TestClient(server_a)


# Teste da rota para listar passagens
def test_listar_passagens():
    response = client.get("/passagens")
    assert response.status_code == HTTP_OK
    assert isinstance(response.json(), list)  # A resposta deve ser uma lista de passagens


# Teste da rota para adicionar uma nova passagem
def test_adicionar_passagem():
    nova_passagem = {
        "origem": "São Paulo",
        "parada": "Rio de Janeiro",
        "destino": "Salvador",
        "disponivel": 10,
    }
    response = client.post("/passagens_a", json=nova_passagem)
    assert response.status_code == HTTP_OK
    assert response.json()["origem"] == nova_passagem["origem"]
    assert response.json()["parada"] == nova_passagem["parada"]
    assert response.json()["destino"] == nova_passagem["destino"]
    assert response.json()["disponivel"] == nova_passagem["disponivel"]


# Teste da rota para buscar uma passagem específica
def test_buscar_passagem():
    # Adiciona uma passagem para que possamos buscar
    nova_passagem = {
        "origem": "São Paulo",
        "parada": "Curitiba",
        "destino": "Florianópolis",
        "disponivel": 5,
    }
    response = client.post("/passagens_a", json=nova_passagem)
    id_passagem = response.json().get("id")

    # Agora busca a passagem
    response = client.get(f"/passagens_a/{id_passagem}")
    assert response.status_code == HTTP_OK
    assert response.json()["origem"] == nova_passagem["origem"]
    assert response.json()["parada"] == nova_passagem["parada"]
    assert response.json()["destino"] == nova_passagem["destino"]


# Teste da venda de uma passagem (do próprio servidor)
def test_vender_passagem_local():
    # Adiciona uma passagem para vender
    nova_passagem = {
        "origem": "São Paulo",
        "parada": "Curitiba",
        "destino": "Florianópolis",
        "disponivel": 10,
    }
    response = client.post("/passagens_a", json=nova_passagem)
    id_passagem = response.json().get("id")

    # Tenta vender a passagem
    response = client.post(f"/vender/{id_passagem}")
    assert response.status_code == HTTP_OK
    assert response.json()["mensagem"] == "Passagem vendida com sucesso!"


# Teste da venda de passagem de outro servidor (Simulando resposta do Servidor B)
def test_venda_de_terceiros():
    # Simula a venda de uma passagem no servidor B
    id_passagem = 1  # Vamos usar um id fixo para o teste
    response = client.post(f"/venda-de-terceiros/b/{id_passagem}")
    assert response.status_code == HTTP_OK
    assert "Resultado da venda" in response.json()


# Teste de consulta aos voos de todos os servidores
def test_consultar_voos():
    response = client.get("/consultar-voos")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert "voss_a" in data
    assert "voos_b" in data
    assert "voos_c" in data


# Teste de resposta dos servidores externos
def test_chamar_servidor_b():
    response = client.get("/chamar-servidor-b/")
    assert response.status_code == HTTP_OK
    assert "dados" in response.json()


def test_chamar_servidor_c():
    response = client.get("/chamar-servidor-c/")
    assert response.status_code == HTTP_OK
    assert "dados" in response.json()

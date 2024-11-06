from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import List
import httpx
import asyncio

server_a = FastAPI()

# Modelo de dados para a passagem_a
class passagem_a(BaseModel):
    origem: str
    parada: str
    destino: str
    disponivel: int = 10  # Campo para verificar se a passagem_a está disponível para venda

locks = {}

# Função para ler passagens_a do arquivo JSON
def ler_passagens_a():
    try:
        with open("passagens_a.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar passagens_a no arquivo JSON
def salvar_passagens_a(passagens_a):
    with open("passagens_a.json", "w") as f:
        json.dump(passagens_a, f, indent=4)

# Rota para listar todas as passagens_a
@server_a.get("/passagens", response_model=List[passagem_a])
def listar_passagens_a():
    passagens_a = ler_passagens_a()
    return list(passagens_a.values())

# Rota para adicionar uma nova passagem_a
@server_a.post("/passagens_a", response_model=passagem_a)
def adicionar_passagem_a(passagem_a: passagem_a):
    passagens_a = ler_passagens_a()
    
    # Verifica se a passagem_a já existe
    id_novo = str(len(passagens_a) + 1)
    if id_novo in passagens_a:
        raise HTTPException(status_code=400, detail="passagem_a já existe.")

    passagens_a[id_novo] = passagem_a.model_dump()
    salvar_passagens_a(passagens_a)
    return passagem_a

# Rota para buscar uma passagem_a específica
@server_a.get("/passagens_a/{id_passagem_a}", response_model=passagem_a)
def buscar_passagem_a(id_passagem_a: str):
    passagens_a = ler_passagens_a()
    passagem_a = passagens_a.get(id_passagem_a)
    if passagem_a is None:
        raise HTTPException(status_code=404, detail="passagem_a não encontrada.")
    return passagem_a

# Rota para realizar a venda de uma passagem_a
@server_a.post("/vender/{id_passagem}")
async def vender_passagem(id_passagem: str):
    passagens = ler_passagens_a()
    passagem = passagens.get(id_passagem)

    if passagem is None:
        raise HTTPException(status_code=404, detail="Passagem não encontrada.")

    # Inicializa um lock para essa passagem se ainda não existir
    if id_passagem not in locks:
        locks[id_passagem] = asyncio.Lock()

    # Tenta adquirir o lock antes de processar a venda
    async with locks[id_passagem]:
        # Verifica novamente a disponibilidade dentro do bloqueio
        if passagem["disponivel"] <= 0:
            raise HTTPException(status_code=400, detail="Passagem não disponível para venda.")

        # Realiza a venda, diminuindo a disponibilidade
        passagem["disponivel"] -= 1
        passagens[id_passagem] = passagem
        salvar_passagens_a(passagens)

    return {"mensagem": "Passagem vendida com sucesso!", "passagem": passagem}

@server_a.get("/chamar-servidor-b/")
async def chamar_servidor_b():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8008/receber-dados/")
    return {"mensagem": "Resposta do Servidor B", "dados": response.json()}


@server_a.get("/chamar-servidor-c/")
async def chamar_servidor_c():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8016/receber-dados/")
    return {"mensagem": "Resposta do Servidor C", "dados": response.json()}


@server_a.get("/receber-dados/")
async def receber_dados():
    return {"mensagem": "Servidor A : Dados recebidos pelos Servidores"}

import httpx

async def consultar_passagens_de(outro_servidor_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{outro_servidor_url}/passagens")
        return response.json()  # Retorna a lista de passagens do servidor consultado

@server_a.get("/consultar-voos")
async def consultar_voos():
    voos_a = listar_passagens_a()
    voos_b = await consultar_passagens_de("http://192.168.0.109:8008")  # Servidor B
    voos_c = await consultar_passagens_de("http://192.168.0.109:8016")  # Servidor C
    return {"voss_a":voos_a,"voos_b": voos_b, "voos_c": voos_c}

async def vender_passagens_de(outro_servidor_url: str, id_passagem: int):
    async with httpx.AsyncClient() as client:
        # Faz uma requisição POST para realizar a venda no outro servidor
        response = await client.post(f"{outro_servidor_url}/vender/{id_passagem}")
        return response.json()  # Retorna o resultado da venda do outro servidor

@server_a.get("/venda-de-terceiros/{id_passagem}")
async def venda_de_terceiros(id_passagem: int):
    # Chama a função para vender a passagem em outro servidor
    resultado_venda = await vender_passagens_de("http://192.168.0.109:8008", id_passagem)
    return {"Resultado da venda": resultado_venda}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server_a, host="192.168.0.109:", port=8000)

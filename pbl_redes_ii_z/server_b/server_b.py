import asyncio
import json
import os
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SERVER_A_URL = os.getenv("SERVER_A_URL", "http://server_a:8004")
SERVER_C_URL = os.getenv("SERVER_C_URL", "http://server_c:8016")




server_b = FastAPI()


class passagem_b(BaseModel):
    origem: str
    parada: str
    destino: str
    disponivel: int = 10  # Campo para verificar se a passagem_a está disponível para venda


locks = {}


# Função para ler passagens_a do arquivo JSON
def ler_passagens_b():
    try:
        # Adicionando o parâmetro encoding="utf-8"
        with open("passagens_b.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Função para salvar passagens_a no arquivo JSON
def salvar_passagens_b(passagens_b):
    # Adicionando o parâmetro encoding="utf-8"
    with open("passagens_b.json", "w", encoding="utf-8") as f:
        json.dump(passagens_b, f, indent=4)


@server_b.get("/passagens", response_model=List[passagem_b])
def listar_passagens_b():
    passagens_b = ler_passagens_b()
    return list(passagens_b.values())


@server_b.post("/passagens_b", response_model=passagem_b)
def adicionar_passagem_b(passagem_b: passagem_b):
    passagens_b = ler_passagens_b()

    # Verifica se a passagem_a já existe
    id_novo = str(len(passagens_b) + 1)
    if id_novo in passagens_b:
        raise HTTPException(status_code=400, detail="passagem_b já existe.")

    passagens_b[id_novo] = passagem_b.model_dump()
    salvar_passagens_b(passagens_b)
    return passagem_b


# Rota para buscar uma passagem_a específica
@server_b.get("/passagens_b/{id_passagem_b}", response_model=passagem_b)
def buscar_passagem_b(id_passagem_b: str):
    passagens_b = ler_passagens_b()
    passagem_b = passagens_b.get(id_passagem_b)
    if passagem_b is None:
        raise HTTPException(status_code=404, detail="passagem_b não encontrada.")
    return passagem_b


@server_b.post("/vender/{id_passagem}")
async def vender_passagem_local(id_passagem: str):
    passagens = ler_passagens_b()
    passagem = passagens.get(id_passagem)

    if passagem is None:
        raise HTTPException(status_code=404, detail="Passagem não encontrada.")

    if id_passagem not in locks:
        locks[id_passagem] = asyncio.Lock()

    async with locks[id_passagem]:
        if passagem["disponivel"] <= 0:
            raise HTTPException(status_code=400, detail="Passagem não disponível para venda.")

        # Realiza a venda
        passagem["disponivel"] -= 1
        passagens[id_passagem] = passagem
        salvar_passagens_b(passagens)

    return {"mensagem": "Passagem vendida com sucesso!", "passagem": passagem}


@server_b.get("/chamar-servidor-a/")
async def chamar_servidor_a():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_A_URL}/receber-dados/")
    return {"mensagem": "Resposta do Servidor A", "dados": response.json()}


@server_b.get("/chamar-servidor-c/")
async def chamar_servidor_c():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_C_URL}/receber-dados/")
    return {"mensagem": "Resposta do Servidor C", "dados": response.json()}


@server_b.get("/receber-dados/")
async def receber_dados():
    return {"mensagem": "Servidor B : Dados recebidos pelos Servidores"}


async def consultar_passagens_de(outro_servidor_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{outro_servidor_url}/passagens")
        return response.json()  # Retorna a lista de passagens do servidor consultado


@server_b.get("/consultar-voos")
async def consultar_voos():
    voos_b = listar_passagens_b()
    try:
        voos_a = await consultar_passagens_de(SERVER_A_URL)  # Servidor A
    except:
        voos_a = []
    try:
        voos_c = await consultar_passagens_de(SERVER_C_URL)  # Servidor C
    except:
        voos_c = []
        
    return {"voss_b": voos_b, "voos_a": voos_a, "voos_c": voos_c}


async def vender_passagens_de(outro_servidor_url: str, id_passagem: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{outro_servidor_url}/vender/{id_passagem}")
        return response.json()  # Retorna o resultado da venda do outro servidor


@server_b.post("/venda-de-terceiros/{id_servidor}/{id_passagem}")
async def venda_de_terceiros(id_servidor: str, id_passagem: str):
    if id_servidor == "b":
        resultado_venda = await vender_passagem_local(id_passagem)
    elif id_servidor == "a":
        resultado_venda = await vender_passagens_de(SERVER_A_URL, id_passagem)
    elif id_servidor == "c":
        resultado_venda = await vender_passagens_de(SERVER_C_URL, id_passagem)
    else:
        return {"erro": "Servidor inválido. Use 'a', 'b' ou 'c' para especificar o servidor."}

    return {"Resultado da venda": resultado_venda}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server_b, host="192.168.0.109:", port=8000)

import asyncio
import json
import os
from typing import List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

SERVER_B_URL = os.getenv("SERVER_B_URL", "http://server_a:8004")
SERVER_C_URL = os.getenv("SERVER_C_URL", "http://server_c:8008")


server_c = FastAPI()


class passagens_c(BaseModel):
    origem: str
    parada: str
    destino: str
    disponivel: int = 10  # Campo para verificar se a passagem_a está disponível para venda


locks = {}


# Função para ler passagens_a do arquivo JSON
def ler_passagens_c():
    try:
        # Adicionando o parâmetro encoding="utf-8"
        with open("passagens_c.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Função para salvar passagens_a no arquivo JSON
def salvar_passagens_c(passagens_c):
    # Adicionando o parâmetro encoding="utf-8"
    with open("passagens_c.json", "w", encoding="utf-8") as f:
        json.dump(passagens_c, f, indent=4)


@server_c.get("/passagens", response_model=List[passagens_c])
def listar_passagens_c():
    passagens_c = ler_passagens_c()
    return list(passagens_c.values())


@server_c.post("/passagens_c", response_model=passagens_c)
def adicionar_passagens_c(passagens_c: passagens_c):
    passagens_c = ler_passagens_c()

    # Verifica se a passagem_a já existe
    id_novo = str(len(passagens_c) + 1)
    if id_novo in passagens_c:
        raise HTTPException(status_code=400, detail="passagem_a já existe.")

    passagens_c[id_novo] = passagens_c.model_dump()
    salvar_passagens_c(passagens_c)
    return passagens_c


# Rota para buscar uma passagem_a específica
@server_c.get("/passagens_c/{id_passagem_c}", response_model=passagens_c)
def buscar_passagens_c(id_passagens_c: str):
    passagens_c = ler_passagens_c()
    passagens_c = passagens_c.get(id_passagens_c)
    if passagens_c is None:
        raise HTTPException(status_code=404, detail="passagem_a não encontrada.")
    return passagens_c


@server_c.post("/vender/{id_passagem}")
async def vender_passagem_local(id_passagem: str):
    passagens = ler_passagens_c()
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
        salvar_passagens_c(passagens)

    return {"mensagem": "Passagem vendida com sucesso!", "passagem": passagem}


@server_c.get("/chamar-servidor-a/")
async def chamar_servidor_a():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_A_URL}/receber-dados/")
    return {"mensagem": "Resposta do Servidor A", "dados": response.json()}


@server_c.get("/chamar-servidor-b/")
async def chamar_servidor_b():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_B_URL}/receber-dados/")
    return {"mensagem": "Resposta do Servidor B", "dados": response.json()}


@server_c.get("/receber-dados/")
async def receber_dados():
    return {"mensagem": "Servidor C : Dados recebidos pelos Servidores"}


async def consultar_passagens_de(outro_servidor_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{outro_servidor_url}/passagens")
        return response.json()  # Retorna a lista de passagens do servidor consultado


@server_c.get("/consultar-voos")
async def consultar_voos():
    voos_c = listar_passagens_c()
    voos_a = await consultar_passagens_de(SERVER_A_URL)  # Servidor A
    voos_c = await consultar_passagens_de(SERVER_B_URL)  # Servidor C
    return {"voss_c": voos_c, "voos_a": voos_a, "voos_b": voos_c}


async def vender_passagens_de(outro_servidor_url: str, id_passagem: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{outro_servidor_url}/vender/{id_passagem}")
        return response.json()  # Retorna o resultado da venda do outro servidor


@server_c.post("/venda-de-terceiros/{id_servidor}/{id_passagem}")
async def venda_de_terceiros(id_servidor: str, id_passagem: str):
    if id_servidor == "c":
        resultado_venda = await vender_passagem_local(id_passagem)
    elif id_servidor == "a":
        resultado_venda = await vender_passagens_de(SERVER_A_URL, id_passagem)
    elif id_servidor == "b":
        resultado_venda = await vender_passagens_de(SERVER_B_URL, id_passagem)
    else:
        return {"erro": "Servidor inválido. Use 'a', 'b' ou 'c' para especificar o servidor."}

    return {"Resultado da venda": resultado_venda}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server_c, host="192.168.0.109:", port=8000)

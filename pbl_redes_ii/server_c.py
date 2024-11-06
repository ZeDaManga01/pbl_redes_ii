from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import List
import httpx
import asyncio

server_c = FastAPI()

# Modelo de dados para a passagem
class Passagem(BaseModel):
    origem: str
    parada: str
    destino: str
    disponivel: int = 10  # Campo para verificar se a passagem está disponível para venda

locks = {}

# Função para ler passagens_c do arquivo JSON
def ler_passagens_c():
    try:
        with open("passagens_c.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar passagens_c no arquivo JSON
def salvar_passagens_c(passagens_c):
    with open("passagens_c.json", "w") as f:
        json.dump(passagens_c, f, indent=4)

# Rota para listar todas as passagens_c
@server_c.get("/passagens", response_model=List[Passagem])
def listar_passagens_c():
    passagens_c = ler_passagens_c()
    return list(passagens_c.values())

# Rota para adicionar uma nova passagem
@server_c.post("/passagens", response_model=Passagem)
def adicionar_passagem(passagem: Passagem):
    passagens_c = ler_passagens_c()
    
    # Verifica se a passagem já existe
    id_novo = str(len(passagens_c) + 1)
    if id_novo in passagens_c:
        raise HTTPException(status_code=400, detail="Passagem já existe.")

    passagens_c[id_novo] = passagem.model_dump()
    salvar_passagens_c(passagens_c)
    return passagem

# Rota para buscar uma passagem específica
@server_c.get("/passagens/{id_passagem}", response_model=Passagem)
def buscar_passagem(id_passagem: str):
    passagens_c = ler_passagens_c()
    passagem = passagens_c.get(id_passagem)
    if passagem is None:
        raise HTTPException(status_code=404, detail="Passagem não encontrada.")
    return passagem

# Rota para realizar a venda de uma passagem
@server_c.post("/vender/{id_passagem}")
async def vender_passagem(id_passagem: str):
    passagens = ler_passagens_c()
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
        salvar_passagens_c(passagens)

    return {"mensagem": "Passagem vendida com sucesso!", "passagem": passagem}


@server_c.get("/chamar-servidor-a/")
async def chamar_servidor_a():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8004/receber-dados/")
    return {"mensagem": "Resposta do Servidor A", "dados": response.json()}


@server_c.get("/chamar-servidor-c/")
async def chamar_servidor_c():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8008/receber-dados/")
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
    voos_a = await consultar_passagens_de("http://192.168.0.109:8004")  # Servidor A
    voos_b = await consultar_passagens_de("http://192.168.0.109:8008")  # Servidor B
    return {"voss_c":voos_c,"voos_a": voos_a, "voos_b": voos_b}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server_c, host="192.168.0.109:", port=8008)

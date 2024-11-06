from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from typing import List
import httpx
import asyncio


server_b = FastAPI()

# Modelo de dados para a passagem
class Passagem(BaseModel):
    origem: str
    parada: str
    destino: str
    disponivel: int = 10  # Campo para verificar se a passagem está disponível para venda

locks = {}

# Função para ler passagens_b do arquivo JSON
def ler_passagens_b():
    try:
        with open("passagens_b.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar passagens_b no arquivo JSON
def salvar_passagens_b(passagens_b):
    with open("passagens_b.json", "w") as f:
        json.dump(passagens_b, f, indent=4)

# Rota para listar todas as passagens_b
@server_b.get("/passagens", response_model=List[Passagem])
def listar_passagens_b():
    passagens_b = ler_passagens_b()
    return list(passagens_b.values())

# Rota para adicionar uma nova passagem
@server_b.post("/passagens", response_model=Passagem)
def adicionar_passagem(passagem: Passagem):
    passagens_b = ler_passagens_b()
    
    # Verifica se a passagem já existe
    id_novo = str(len(passagens_b) + 1)
    if id_novo in passagens_b:
        raise HTTPException(status_code=400, detail="Passagem já existe.")

    passagens_b[id_novo] = passagem.model_dump()
    salvar_passagens_b(passagens_b)
    return passagem

# Rota para buscar uma passagem específica
@server_b.get("/passagens/{id_passagem}", response_model=Passagem)
def buscar_passagem(id_passagem: str):
    passagens_b = ler_passagens_b()
    passagem = passagens_b.get(id_passagem)
    if passagem is None:
        raise HTTPException(status_code=404, detail="Passagem não encontrada.")
    return passagem

# Rota para realizar a venda de uma passagem
@server_b.post("/vender/{id_passagem}")
async def vender_passagem(id_passagem: str):
    passagens = ler_passagens_b()
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
        salvar_passagens_b(passagens)

    return {"mensagem": "Passagem vendida com sucesso!", "passagem": passagem}



@server_b.get("/chamar-servidor-a/")
async def chamar_servidor_a():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8004/receber-dados/")
    return {"mensagem": "Resposta do Servidor A", "dados": response.json()}


@server_b.get("/chamar-servidor-c/")
async def chamar_servidor_c():
    async with httpx.AsyncClient() as client:

        response = await client.get("http://192.168.0.109:8016/receber-dados/")
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
    voos_a = await consultar_passagens_de("http://192.168.0.109:8004")  # Servidor A
    voos_c = await consultar_passagens_de("http://192.168.0.109:8016")  # Servidor C
    return {"voss_b":voos_b,"voos_a": voos_a, "voos_c": voos_c}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server_b, host="192.168.0.109:", port=8004)

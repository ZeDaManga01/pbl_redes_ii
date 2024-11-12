import asyncio
import json
import os
from typing import List
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

#SERVER_A_URL = os.getenv("SERVER_A_URL", "http://server_a:8004")
#SERVER_B_URL = os.getenv("SERVER_B_URL", "http://server_b:8008")
#SERVER_C_URL = os.getenv("SERVER_C_URL", "http://server_c:8016")

SERVER_A_URL = os.getenv("SERVER_A_URL", "http://localhost:8004")
SERVER_B_URL = os.getenv("SERVER_B_URL", "http://localhost:8008")
SERVER_C_URL = os.getenv("SERVER_C_URL", "http://localhost:8016")

server_a = FastAPI()


# Modelo de dados para a passagem_a
class passagem_a(BaseModel):
    id: int
    cidade: str
    preco: float
    disponivel: int = 10  

locks = {}

# Função para ler passagens_a do arquivo JSON
def ler_passagens_a():
    try:
        # Adicionando o parâmetro encoding="utf-8"
        with open("pbl_redes_ii_z\\server_a\\passagens_a.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
@server_a.get("/ler-passagens")
def ler_passagens_get():
    try:
        # Adicionando o parâmetro encoding="utf-8"
        with open("pbl_redes_ii_z\\server_a\\passagens_a.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@server_a.post("/salvar-passagem")
def salvar_passagens_poscompra(passagem: dict):
    # Abrir o arquivo JSON no modo leitura/escrita
    with open("pbl_redes_ii_z\\server_a\\passagens_a.json", "r+") as f:
        # Carregar as passagens existentes
        passagens = json.load(f)

        # Procurar o trecho com o ID correspondente e atualizar os valores diretamente
        for chave, trecho in passagens.items():
            if trecho['id'] == passagem['passagem']['id']:
                # Atualizar cada campo do trecho diretamente
                trecho['cidade'] = passagem['passagem'].get('cidade', trecho['cidade'])
                trecho['preco'] = passagem['passagem'].get('preco', trecho['preco'])
                trecho['disponivel'] = passagem['passagem'].get('disponivel', trecho['disponivel'])
        
        # Sobrescrever o arquivo com as novas informações
        f.seek(0)
        json.dump(passagens, f, indent=4)
        f.truncate()  # Limpar o restante do arquivo caso o novo conteúdo seja menor

def salvar_passagens_a(passagens_a):
    # Adicionando o parâmetro encoding="utf-8"
    with open("pbl_redes_ii_z\\server_a\\passagens_a.json", "w", encoding="utf-8") as f:
        json.dump(passagens_a, f, indent=4)



# Rota para listar todas as passagens_a
@server_a.get("/passagens", response_model=List[passagem_a])
def listar_passagens_a():
    passagens_a = ler_passagens_a()
    # Converte o dicionário em uma lista de valores para que possa ser retornado como JSON
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
@server_a.get("/passagens_a", response_model=passagem_a)
async def buscar_passagem_por_id(id_server:str ,id_trecho: int):
    if id_server == 'a':
        try:
            # Abrir o arquivo JSON
            trechos = ler_passagens_a()
            # Procurar pelo ID na lista de passagens
            for chave, passagem in trechos.items():
                if passagem['id'] == id_trecho:
                    return passagem  # Retorna a passagem encontrada
            return None  # Se não encontrar, retorna None       
        except FileNotFoundError:
            print(f"Arquivo {trechos} não encontrado.")
            return None
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON.")
            return None
    elif id_server == 'b':
        try:
            # Abrir o arquivo JSON
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SERVER_B_URL}/ler-passagens")
                trechos = response.json()
            # Procurar pelo ID na lista de passagens
            for chave, passagem in trechos.items():
                if passagem['id'] == id_trecho:
                    return passagem  # Retorna a passagem encontrada
        except FileNotFoundError:
            print(f"Arquivo {trechos} não encontrado.")
            return None
        
    elif id_server == 'c':
        try:
            # Abrir o arquivo JSON
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{SERVER_C_URL}/ler-passagens")
                trechos = response.json()
            # Procurar pelo ID na lista de passagens
            for chave, passagem in trechos.items():
                if passagem['id'] == id_trecho:
                    return passagem  # Retorna a passagem encontrada
        except FileNotFoundError:
            print(f"Arquivo {trechos} não encontrado.")
            return None
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON.")
            return None
    
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo JSON.")
            return None
        
async def comprar_passagem(id_passagem: str, id_trecho: int):
    # Chama a função para buscar a passagem
    response = await buscar_passagem_por_id(id_passagem, id_trecho)
    
    # Diminui a quantidade disponível da passagem
    if response['disponivel'] > 0:
        response['disponivel'] -= 1
        
        # Salva os dados atualizados, chamando o endpoint correto dependendo do servidor
        if id_passagem == 'a':
            # Envia a passagem atualizada para o servidor A
            async with httpx.AsyncClient() as client:
                salvamento = await client.post(
                    f"http://localhost:8004/salvar-passagem",
                    json={"passagem": response}
                )
        elif id_passagem == 'b':
            # Envia a passagem atualizada para o servidor B
            async with httpx.AsyncClient() as client:
                salvamento = await client.post(
                    f"{SERVER_B_URL}/salvar-passagem",
                    json={"passagem": response}
                )
        elif id_passagem == 'c':
            # Envia a passagem atualizada para o servidor C
            async with httpx.AsyncClient() as client:
                salvamento = await client.post(
                    f"{SERVER_C_URL}/salvar-passagem",
                    json={"passagem": response}
                )

        print(f"Passagem {id_passagem} (trecho {id_trecho}) comprada! Disponíveis agora: {response['disponivel']}")
        return True

    return False

       
# Função auxiliar para verificar se a passagem está disponível
async def verificar_disponibilidade(id_passagem: str, id_trecho: int):
    # Aqui você deve buscar a passagem, por exemplo, a partir de um banco de dados ou arquivo JSON
    passagem = await buscar_passagem_por_id(id_passagem, id_trecho)
    
    if passagem and passagem['disponivel'] > 0:
        return True, passagem  # Retorna True e a passagem com todos os detalhes, incluindo o preço
    else:
        return False, passagem  # Retorna False caso a passagem não esteja disponível
    
@server_a.post("/comprar-rota")
async def comprar_rota(id_passagem_p1: str, id_trecho_p1: int, id_passagem_p2: str, id_trecho_p2: int, id_passagem_p3: str, id_trecho_p3: int):
    # Criando uma lista de tuplas com os dados
    info_rota = [(id_passagem_p1, id_trecho_p1), (id_passagem_p2, id_trecho_p2), (id_passagem_p3, id_trecho_p3)]
    
    # Variáveis para armazenar o status de disponibilidade de todas as passagens
    passagens_disponiveis = True
    respostas = []
    total_preco = 0  # Variável para acumular o preço total das passagens

    # Primeiro, verificar a disponibilidade de todas as passagens
    for id_passagem, id_trecho in info_rota:
        disponibilidade, response = await verificar_disponibilidade(id_passagem, id_trecho)
        
        if disponibilidade:
            respostas.append(f"Passagem {id_passagem} (trecho {id_trecho}) está disponível! Preço: {response['preco']}")
            total_preco += response['preco']  # Adiciona o preço da passagem ao total
        else:
            passagens_disponiveis = False
            respostas.append(f"Passagem {id_passagem} (trecho {id_trecho}) está esgotada.")

    # Se todas as passagens estão disponíveis, efetuar a compra
    if passagens_disponiveis:
        for id_passagem, id_trecho in info_rota:
            sucesso = await comprar_passagem(id_passagem, id_trecho)
            if not sucesso:
                return {"mensagem": "Erro ao comprar passagem, tente novamente.", "detalhes": respostas}

        return {
            "mensagem": "Compra realizada com sucesso!",
            "detalhes": respostas,
            "valor_total": total_preco  # Exibe o valor total da compra
        }
    
    else:
        return {"mensagem": "Algumas passagens estão esgotadas.", "detalhes": respostas}



async def consultar_passagens_de(outro_servidor_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{outro_servidor_url}/passagens")
        return response.json()  # Retorna a lista de passagens do servidor consultado


@server_a.get("/consultar-voos")
async def consultar_voos():
    voos_a = listar_passagens_a()
    try:
        voos_b = await consultar_passagens_de(SERVER_B_URL)  # Servidor A
    except:
        voos_b = []
    try:
        voos_c = await consultar_passagens_de(SERVER_C_URL)  # Servidor C
    except:
        voos_c = []
    return {"voss_a": voos_a, "voos_b": voos_b, "voos_c": voos_c}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server_a, host="192.168.0.109:", port=8004)

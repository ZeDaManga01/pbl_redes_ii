# Use uma imagem oficial do Python como imagem base
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos para dentro do contêiner
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do seu aplicativo para o contêiner
COPY . /app

# Exponha a porta em que o servidor FastAPI vai rodar
EXPOSE 8008

# Defina o comando para rodar o servidor FastAPI
CMD ["uvicorn", "main:server_a", "--host", "0.0.0.0", "--port", "8008"]

# Use uma imagem Python base
FROM python:3.10-slim

# Defina o diretório de trabalho
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Defina as variáveis de ambiente
ENV PYTHONUNBUFFERED=1

COPY . .

# Execute o script no contêiner
CMD ["sh", "run.sh"]

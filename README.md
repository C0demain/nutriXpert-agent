# nutriXpert-agent

## Descrição
projeto do agente para a api do sexto semestres de análise e desenvolvimento de sistemas

## Pré-requisitos
Python, banco de dados de sua preferencia(neste caso será usado postgres)

## Como rodar o projeto
como iniciar o projeto localmente.
recomendado utilizar um ambiente virtual python para instalar as dependencias

```bash
python -m venv .venv
pip install -r requirements.txt

```

## Configurando o agente

se for utilizar somente para teste sem a necessidade do modelo medgemma, troque no arquivo agent.py o model, existe um comentário explicando no arquivo. Por padrão esta como a variavel de ambiente ADK_MODEL

para rodar com o medgemma o modo que esta estruturado o projeto sera necessario rodar localmente utilizando o ollama,
utilize o modelfile no projeto para criar o mesmo.


## Utilizando Docker (opcional)
Se desejar rodar com Docker

```bash
# Exemplo: Usando Docker Compose
docker-compose up --build
```

## Variáveis de ambiente

das variaveis de ambiete, as mais importantes são adicionar sua API_KEY que pode ser pega em https://aistudio.google.com/app/apikey,
sera necessario criar um projeto para isso.

e adaptar sua DATABASE_URL para o que for ser utilizado, o exemplo abaixo utiliza os dados do docker-compose

o ADK_MODEL esta como gemini-2.0-flash pois é gratuito com a api key gratis

```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_API_KEY

FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
UVICORN_RELOAD=true


ADK_APP_NAME=nutriXpert
DATABASE_URL=postgresql+psycopg2://myuser:mypassword@localhost:5432/mydb
ADK_MODEL=gemini-2.0-flash
ADK_SERIALIZE_RUNNER=false


```


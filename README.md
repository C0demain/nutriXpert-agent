
# nutriXpert-agent

## 📌 Descrição

O **nutriXpert-agent** é um agente conversacional desenvolvido em **Python + FastAPI**, como parte do projeto do 6º semestre de **Análise e Desenvolvimento de Sistemas**.
Ele responde perguntas relacionadas à **nutrição, hábitos alimentares e composição nutricional de alimentos**, utilizando **RAG (Retrieval-Augmented Generation)** para enriquecer suas respostas com base em documentos locais (ex.: PDFs e planilhas TACO).

---

## ⚙️ Pré-requisitos

* **Python 3.10+**
* **PostgreSQL** (ou outro banco compatível, configurado via `DATABASE_URL`)
* (Opcional) **Docker** para containerização
* (Opcional) **Ollama** para rodar modelos locais, como o **MedGemma**

---

## 🚀 Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/nutriXpert-agent.git
cd nutriXpert-agent
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o servidor local

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Executar ADK Web UI para testes
```bash
adk web
```

O projeto estará acessível em:
📍 **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
📍 **Redoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐳 Utilizando Docker (opcional)

Se preferir rodar via containers:

```bash
docker-compose up --build
```

---

## 🔑 Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```ini
# Google API (opcional para usar modelos Gemini)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_API_KEY

# Configuração do FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
UVICORN_RELOAD=true

# Configuração do agente
ADK_APP_NAME=nutriXpert
DATABASE_URL=postgresql+psycopg2://myuser:mypassword@localhost:5432/mydb
ADK_MODEL=gemini-2.0-flash   # ou "ollama_chat/medgemma-4b" se usar via Ollama
ADK_SERIALIZE_RUNNER=false
```

🔗 Sua API Key do Google pode ser gerada em: [Google AI Studio](https://aistudio.google.com/app/apikey).
💡 O modelo padrão é o **Gemini 2.0 Flash**, gratuito no plano básico do Google AI Studio.

---

## 🧠 Implementação do RAG

1. **Ingestão de documentos**

   * Arquivos PDF e XLSX devem ser colocados na pasta `documents/`.
   * A ingestão ocorre automaticamente no primeiro startup.

2. **Vetorização**

   * O conteúdo é dividido em *chunks* pelo `RecursiveCharacterTextSplitter`.
   * Os embeddings são gerados com **HuggingFace (sentence-transformers/all-MiniLM-L6-v2)**.

3. **Armazenamento**

   * Os vetores são persistidos no **ChromaDB** (pasta `chroma_store/`).

4. **Recuperação (Retriever)**

   * Ao receber uma pergunta, o agente busca os *chunks* mais relevantes no ChromaDB.
   * O contexto recuperado é injetado antes da resposta final do modelo.

---

## 🧩 Usando o MedGemma via Ollama

Se preferir rodar o agente com o **MedGemma** localmente:

1. **Instalar o Ollama**
   Baixe em: [https://ollama.com/download](https://ollama.com/download)
   Verifique a instalação:

   ```bash
   ollama --version
   ```

2. **Usar um Modelfile**
   Na raiz do projeto, certifique que existe o arquivo chamado `Modelfile` com o conteúdo:

   ```dockerfile
   FROM hf.co/unsloth/medgemma-4b-it-GGUF:Q4_K_M
   ```

   Esse comando usa a versão quantizada Q4_K_M publicada no Hugging Face.

3. **Registrar o modelo no Ollama**

   ```bash
   ollama create medgemma-4b -f Modelfile
   ```

   Confirme se foi criado:

   ```bash
   ollama list
   ```

4. **Executar o modelo diretamente** (teste opcional):

   ```bash
   ollama run medgemma-4b
   ```

5. **Configurar o agente para usar o MedGemma**
   No arquivo `.env`, altere a linha do modelo para:

   ```ini
   ADK_MODEL=ollama_chat/medgemma-4b
   ```

Agora o NutriXpert rodará utilizando o **MedGemma** local via Ollama.

---

## Observações

* Se quiser rodar com **Gemini** (default), mantenha `ADK_MODEL=gemini-2.0-flash`.
* Se quiser rodar com **MedGemma**, precisa do **Ollama** instalado e do **Modelfile** configurado.
* Se os documentos forem alterados, é necessário **deletar a pasta `chroma_store/`** e reiniciar a aplicação para regenerar os embeddings.


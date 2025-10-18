# nutriXpert-agent

## Descrição

O **nutriXpert-agent** é um agente conversacional inteligente desenvolvido em **Python + FastAPI**, como parte do projeto do 6º semestre de **Análise e Desenvolvimento de Sistemas**.

Ele responde perguntas sobre **nutrição, hábitos alimentares e composição nutricional de alimentos**, utilizando **RAG (Retrieval-Augmented Generation)** para combinar **contexto extraído de documentos locais** (como PDFs da TACO e outros materiais de referência) com **modelos de linguagem** — podendo rodar **Gemini 2.0 Flash** (Google AI) ou **MedGemma** (via Ollama).


## Pré-requisitos

* **Python 3.10+**
* **PostgreSQL** (ou outro banco compatível, configurado via `DATABASE_URL`)


## Como rodar o projeto

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

### 5. (Opcional) Executar o ADK Web UI

```bash
adk web
```

**Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
**Redoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)


## Rodando com Docker

```bash
docker-compose up --build
```

## Variáveis de ambiente

Crie o arquivo `.env` na raiz:

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
ADK_MODEL=gemini-2.0-flash
ADK_SERIALIZE_RUNNER=false
```

🔗 Gere sua API Key em [Google AI Studio](https://aistudio.google.com/app/apikey).
O modelo padrão é o **Gemini 2.0 Flash**, gratuito no plano básico.

---

## Estrutura do Banco de Dados SQL

O **nutriXpert-agent** utiliza o **SQLAlchemy ORM** integrado com o **Google ADK**, o que significa que algumas tabelas são **criadas automaticamente** pelo ADK e outras **foram definidas manualmente** para o projeto.

### **Tabelas criadas automaticamente pelo ADK**

Essas tabelas são gerenciadas internamente pelo **SessionService** e **StateManager** do ADK.
Você **não precisa criar nem mapear manualmente** — elas são criadas automaticamente no banco configurado em `DATABASE_URL`.

| Tabela        | Finalidade                                                                      | Gerenciada pelo ADK |
| ------------- | ------------------------------------------------------------------------------- | ------------------- |
| `sessions`    | Armazena o histórico completo das conversas (mensagens do usuário e do agente). | ✅                   |
| `events`      | Guarda eventos de estado e ações internas do agente.                            | ✅                   |
| `user_states` | Estado persistente de cada usuário (memória de longo prazo).                    | ✅                   |
| `app_states`  | Estado global do aplicativo (configurações do agente).                          | ✅                   |

Essas tabelas são usadas para restaurar contextos e estados entre sessões e garantir que o agente "lembre" informações mesmo após o restart.

---

### **Tabelas criadas manualmente pelo projeto**

| Tabela           | Finalidade                                                                                         | Gerenciada pelo ADK |
| ---------------- | -------------------------------------------------------------------------------------------------- | ------------------- |
| `alimentos_taco` | Tabela de alimentos com composição nutricional baseada na base TACO (usada nas consultas via RAG). | ❌                   |
| `feedbacks`      | Tabela de feedbacks de usuários sobre respostas do agente (Human-in-the-Loop).                     | ❌                   |

Essas tabelas são definidas no código Python (via SQLAlchemy models) e são parte essencial do aprendizado contínuo do agente.

---

## Human in the Loop (HITL)

O sistema implementa um mecanismo de **aprendizado contínuo com feedback humano** (Human-in-the-Loop).

### Como funciona

1. Cada vez que o agente responde algo, o frontend exibe opções de feedback ao usuário:

   * Uma **nota (0 a 5)** para avaliar a qualidade da resposta.
   * Um campo para o usuário indicar se **“atendeu às expectativas”**.
   * Um **comentário opcional**.

2. O frontend então **envia esse feedback** para a rota:

   ```http
   POST /feedback
   ```

   Com um corpo JSON no formato:

   ```json
   {
     "message_id": "uuid_da_resposta",
     "user_id": "user_test",
     "nota": 5,
     "atendeu_expectativas": true,
     "comentario": "A resposta foi excelente e muito clara!"
   }
   ```

3. O backend salva o feedback no banco e o **adiciona ao ChromaDB (vector store)**, gerando embeddings do comentário.

4. Em futuras perguntas do **mesmo usuário**, o agente recupera automaticamente **feedbacks anteriores** com base na similaridade semântica (via `SentenceTransformer`), utilizando:

   ```python
   search_related_feedbacks(query, user_id)
   ```

5. O agente injeta esses feedbacks relevantes no **prompt do modelo**, adaptando o tom e nível de detalhe das respostas futuras.

---

### Escopo do aprendizado

Os feedbacks são **personalizados por usuário**:

* O aprendizado ocorre **apenas dentro da sessão e histórico daquele `user_id`**.
* As próximas respostas do agente serão ajustadas conforme as preferências e feedbacks individuais do usuário.

Isso garante um comportamento adaptativo e uma experiência personalizada sem afetar outros usuários.

---

### Garantias de integridade

* Cada `message_id` (resposta do agente) só pode receber **um único feedback por usuário**.
* Caso o usuário tente enviar outro feedback para a mesma resposta, a API retorna:

  ```json
  { "detail": "Já existe um feedback para esta resposta." }
  ```

## RAG — Retrieval-Augmented Generation

O NutriXpert utiliza **RAG** para enriquecer as respostas com dados reais:

1. **Ingestão de documentos**: PDFs e planilhas colocados em `documents/` são indexados automaticamente.
2. **Divisão em chunks** com `RecursiveCharacterTextSplitter`.
3. **Geração de embeddings** usando `sentence-transformers/all-MiniLM-L6-v2`.
4. **Armazenamento** no **ChromaDB**.
5. **Recuperação** dinâmica durante cada pergunta, unindo:

   * Contexto dos documentos
   * Feedbacks anteriores
   * Pergunta atual


## Conclusão

O **NutriXpert Agent** combina:

* **RAG** (busca de conhecimento real de documentos)
* **ADK Session Memory** (memória de sessão persistente)
* **Human-in-the-Loop Feedback** (aprendizado personalizado por usuário)

Cada usuário passa a ter uma experiência **personalizada**, com respostas cada vez mais adequadas às suas preferências e feedbacks.


## Exemplo ADK Web

![Interface do ADK Web - exemplo 1](./imgs-readme/adk-web-example-1.png)
![Interface do ADK Web - exemplo 2](./imgs-readme/adk-web-example-2.png)
---

### Exemplo de fluxo completo

1. Usuário pergunta:
   `Explique rapidamente o que é proteína.`
2. O agente responde.
3. O frontend envia um `POST /feedback` com nota e comentário.
4. O backend armazena o feedback e gera embeddings.
5. Nas próximas perguntas do mesmo usuário, o agente ajusta automaticamente o tom e nível de detalhe.
# Ingestão e busca semântica com LangChain e PostgreSQL

Este projeto lê `document.pdf`, divide o texto em chunks de 1000 caracteres com sobreposição de 150, grava embeddings no PostgreSQL com pgVector e responde perguntas no terminal. A busca recupera até 10 chunks e envia ao modelo o prompt exigido pelo desafio. Quando a informação não está no contexto, a resposta esperada é `Não tenho informações necessárias para responder sua pergunta.`

## Preparação

É necessário ter Python 3.12, Docker com Compose e uma chave da OpenAI ou do Google Gemini. Na raiz do repositório:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha as variáveis necessárias em `.env`. O arquivo é ignorado pelo Git. Por padrão, o projeto usa OpenAI com `text-embedding-3-small` e `gpt-4.1-mini`. Para Gemini, use `AI_PROVIDER=gemini`, `GOOGLE_API_KEY` e, se desejar, defina os modelos; os padrões são `models/gemini-embedding-001` e `gemini-2.5-flash`. Confirme a disponibilidade dos modelos na sua conta: [modelos OpenAI](https://platform.openai.com/docs/models) e [modelos Gemini](https://ai.google.dev/gemini-api/docs/models).

| Variável | Uso | Padrão quando vazia |
| --- | --- | --- |
| `AI_PROVIDER` | `openai` ou `gemini` | `openai` |
| `OPENAI_API_KEY` | Chave para OpenAI | obrigatória para OpenAI |
| `OPENAI_BASE_URL` | Endpoint compatível com OpenAI | endpoint oficial da OpenAI |
| `OPENAI_EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `OPENAI_CHAT_MODEL` | Modelo de chat | `gpt-4.1-mini` |
| `GOOGLE_API_KEY` | Chave para Gemini | obrigatória para Gemini |
| `GOOGLE_EMBEDDING_MODEL` | Modelo de embeddings | `models/gemini-embedding-001` |
| `GOOGLE_CHAT_MODEL` | Modelo de chat | `gemini-2.5-flash` |
| `DATABASE_URL` | Conexão SQLAlchemy com psycopg | `postgresql+psycopg://postgres:postgres@localhost:5432/rag` |
| `PG_VECTOR_COLLECTION_NAME` | Nome da coleção vetorial | `document_pdf` |
| `PDF_PATH` | Caminho do PDF | `document.pdf` deste repositório |

## Execução

```bash
docker compose up -d
python src/ingest.py
python src/chat.py
```

Digite uma pergunta após `PERGUNTA:` e use `sair` para encerrar. Por exemplo, pergunte `Qual o faturamento da Empresa SuperTechIABrazil?`. O valor registrado no PDF é R$ 10.000.000,00. A ingestão informa quantos chunks foram gravados.

Se a porta 5432 já estiver ocupada, use um arquivo de override fora deste repositório para mapear outra porta e ajuste `DATABASE_URL` para a mesma porta. O `docker-compose.yml` entregue mantém a porta 5432.

**Atenção:** use o mesmo modelo de embeddings na ingestão e na consulta. Modelos diferentes podem gerar vetores com dimensões incompatíveis; para trocar de modelo, recrie a coleção e ingira o PDF novamente. Executar a ingestão repetidamente acrescenta novos registros à coleção.

"""Busca vetorial e resposta restrita ao conteúdo do PDF."""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

FALLBACK_ANSWER = "Não tenho informações necessárias para responder sua pergunta."

PROMPT_TEMPLATE = """CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"""


def provider():
    name = os.getenv("AI_PROVIDER", "openai").strip().lower()
    if name not in {"openai", "gemini"}:
        raise ValueError("AI_PROVIDER deve ser 'openai' ou 'gemini'.")
    return name


def embeddings():
    if provider() == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Defina GOOGLE_API_KEY para usar Gemini.")
        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL") or "models/gemini-embedding-001"
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Defina OPENAI_API_KEY para usar OpenAI.")
    options = {"model": os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small"}
    if os.getenv("OPENAI_BASE_URL"):
        options["base_url"] = os.environ["OPENAI_BASE_URL"]
    return OpenAIEmbeddings(**options)


def vector_store():
    return PGVector(
        embeddings=embeddings(),
        connection=os.getenv("DATABASE_URL") or "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME") or "document_pdf",
        use_jsonb=True,
    )


def chat_model():
    if provider() == "gemini":
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_CHAT_MODEL") or "gemini-2.5-flash",
            temperature=0,
        )

    options = {
        "model": os.getenv("OPENAI_CHAT_MODEL") or "gpt-4.1-mini",
        "temperature": 0,
    }
    if os.getenv("OPENAI_BASE_URL"):
        options["base_url"] = os.environ["OPENAI_BASE_URL"]
    return ChatOpenAI(**options)


def search_prompt(question=None):
    """Cria uma função de perguntas, reutilizando banco e modelo durante o chat."""
    store = vector_store()
    model = chat_model()

    def answer(user_question):
        matches = store.similarity_search_with_score(user_question, k=10)
        context = "\n\n".join(document.page_content for document, _score in matches)
        if not context.strip():
            return FALLBACK_ANSWER

        response = model.invoke(PROMPT_TEMPLATE.format(contexto=context, pergunta=user_question))
        result = response.content.strip()
        if FALLBACK_ANSWER in result:
            return FALLBACK_ANSWER
        return result

    return answer(question) if question is not None else answer

"""Carrega o PDF, divide em chunks e grava seus vetores no PostgreSQL."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from search import vector_store

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def ingest_pdf():
    pdf_path = Path(os.getenv("PDF_PATH") or PROJECT_ROOT / "document.pdf")
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    pages = PyPDFLoader(str(pdf_path)).load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    ).split_documents(pages)
    if not chunks:
        raise ValueError("O PDF não contém texto para ingestão.")

    vector_store().add_documents(chunks)
    print(f"Ingestão concluída: {len(chunks)} chunks gravados de {len(pages)} páginas.")
    return len(chunks)


if __name__ == "__main__":
    ingest_pdf()

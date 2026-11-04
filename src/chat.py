"""Interface de perguntas e respostas no terminal."""

from search import search_prompt


def main():
    try:
        answer = search_prompt()
    except (ValueError, OSError) as error:
        print(f"Não foi possível iniciar o chat: {error}")
        return

    print("Faça sua pergunta (ou digite 'sair' para encerrar):")
    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"sair", "exit", "quit"}:
            break
        if not question:
            continue

        try:
            print(f"RESPOSTA: {answer(question)}")
        except Exception as error:
            print(f"Erro ao consultar o documento: {error}")


if __name__ == "__main__":
    main()

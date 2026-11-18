from pathlib import Path

from assistente import Assistente, ler_opcao
from base_conhecimento import BaseConhecimento
from energia import menu_energia


def main(diretorio_dados=None):
    if diretorio_dados is None:
        diretorio_dados = Path(__file__).resolve().parent / "data"
    diretorio_dados = Path(diretorio_dados)
    base = BaseConhecimento(diretorio_dados / "base_conhecimento.json")
    assistente = Assistente("Citizen Assist AI", base, diretorio_dados / "historico.json")

    print(f"\n{assistente.nome} — Primeiros passos no SUS")
    print("Orientações administrativas para quem está começando a usar o SUS.")
    try:
        while True:
            print("\n1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos para CSV")
            print("5. Energia e sustentabilidade")
            print("0. Sair")
            opcao = ler_opcao(5)
            if opcao == 0:
                print("\nDe 1 (difícil) a 5 (fácil), como foi usar o assistente?")
                print("0. Voltar ao menu")
                nota = ler_opcao(5, "Nota: ")
                if nota:
                    assistente.registrar_facilidade(nota)
                    print("Obrigado por usar o assistente.")
                    return
            elif opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.exibir_indicadores()
            elif opcao == 5:
                menu_energia()
            else:
                assistente.exportar_csv(diretorio_dados / "atendimentos.csv")
    except (EOFError, KeyboardInterrupt):
        print("\nSessão encerrada.")


if __name__ == "__main__":
    main()

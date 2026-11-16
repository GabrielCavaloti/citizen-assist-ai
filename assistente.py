import csv
import json
import math
import tempfile
import time
from datetime import datetime
from pathlib import Path


CAMPOS_CSV = (
    "data", "origem", "pergunta", "orientacao_id",
    "encontrou", "ajudou", "tentativas", "tempo_segundos",
)


def ler_opcao(maximo, mensagem="Escolha: "):
    opcoes = {str(numero): numero for numero in range(maximo + 1)}
    while True:
        entrada = input(mensagem).strip()
        if entrada in opcoes:
            return opcoes[entrada]
        print(f"Opção inválida. Digite um número de 0 a {maximo}.")


def contem_dado_pessoal(texto):
    return "@" in texto or sum(caractere.isdigit() for caractere in texto) >= 8


class Assistente:
    def __init__(self, nome, base, caminho_historico):
        self.nome = nome
        self.base = base
        self.caminho_historico = Path(caminho_historico)
        self.historico = []
        self.notas_facilidade = []
        self.historico_disponivel = True
        self._carregar_historico()

    def _carregar_historico(self):
        try:
            dados = json.loads(self.caminho_historico.read_text(encoding="utf-8-sig"))
            if isinstance(dados, list):
                atendimentos, notas = dados, []
            elif isinstance(dados, dict):
                atendimentos = dados["atendimentos"]
                notas = dados["notas_facilidade"]
            else:
                raise ValueError("estrutura inválida")
            if not isinstance(atendimentos, list) or not all(
                self._atendimento_valido(a) for a in atendimentos
            ):
                raise ValueError("atendimentos inválidos")
            if not isinstance(notas, list) or not all(
                type(nota) is int and 1 <= nota <= 5 for nota in notas
            ):
                raise ValueError("notas de facilidade inválidas")
            self.historico = atendimentos
            self.notas_facilidade = notas
        except FileNotFoundError:
            pass  # O primeiro registro cria o arquivo.
        except (OSError, ValueError, KeyError, OverflowError):
            self.historico_disponivel = False
            print("Histórico indisponível. O arquivo original foi preservado e esta sessão usa memória.")

    @staticmethod
    def _atendimento_valido(atendimento):
        if not isinstance(atendimento, dict) or not all(
            campo in atendimento for campo in CAMPOS_CSV
        ):
            return False
        tempo = atendimento["tempo_segundos"]
        return (
            isinstance(atendimento["data"], str)
            and atendimento["origem"] in ("pergunta", "categoria")
            and isinstance(atendimento["pergunta"], str)
            and not contem_dado_pessoal(atendimento["pergunta"])
            and (atendimento["orientacao_id"] is None or isinstance(atendimento["orientacao_id"], str))
            and type(atendimento["encontrou"]) is bool
            and (atendimento["ajudou"] is None or type(atendimento["ajudou"]) is bool)
            and type(atendimento["tentativas"]) is int
            and atendimento["tentativas"] >= 1
            and type(tempo) in (int, float)
            and math.isfinite(tempo)
            and tempo >= 0
        )

    def _salvar_historico(self):
        if not self.historico_disponivel:
            return
        temporario = None
        try:
            self.caminho_historico.parent.mkdir(parents=True, exist_ok=True)
            dados = {"atendimentos": self.historico, "notas_facilidade": self.notas_facilidade}
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.caminho_historico.parent,
                delete=False, suffix=".tmp",
            ) as arquivo:
                temporario = Path(arquivo.name)
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                arquivo.write("\n")
            temporario.replace(self.caminho_historico)
        except OSError:
            print("Não foi possível salvar o histórico. Os registros continuam disponíveis nesta sessão.")
        finally:
            if temporario is not None:
                try:
                    temporario.unlink(missing_ok=True)
                except OSError:
                    pass

    def _selecionar_orientacao(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Nenhuma categoria disponível.")
            return None
        while True:
            print("\nCategorias")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero}. {categoria}")
            print("0. Voltar")
            escolha = ler_opcao(len(categorias))
            if escolha == 0:
                return None
            orientacoes = self.base.por_categoria(categorias[escolha - 1])
            print(f"\n{categorias[escolha - 1]}")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"{numero}. {orientacao.titulo}")
            print("0. Voltar às categorias")
            escolha = ler_opcao(len(orientacoes))
            if escolha:
                return orientacoes[escolha - 1]

    @staticmethod
    def _feedback():
        while True:
            resposta = input("A orientação ajudou? (s/n, 0 para pular e voltar): ").strip().lower()
            if resposta == "0":
                return None
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Resposta inválida. Digite s, n ou 0.")

    def perguntar(self):
        if not self.base.orientacoes:
            print("Nenhuma orientação disponível para busca.")
            return

        inicio = time.time()
        pergunta = ""
        tentativas = 0
        print("\nDescreva sua dúvida sem dados pessoais. Digite 0 para voltar.")
        while True:
            entrada = input("Pergunta: ").strip()
            if entrada == "0":
                if tentativas:
                    self.registrar("pergunta", pergunta, None, None, tentativas, time.time() - inicio)
                return
            if contem_dado_pessoal(entrada):
                print("Pergunta recusada por conter @ ou oito ou mais dígitos. Tente sem esses dados.")
                continue
            if not any(caractere.isalnum() for caractere in entrada):
                print("Digite uma pergunta com palavras.")
                continue

            pergunta = entrada
            tentativas += 1
            resultados = [(pontos, o) for pontos, o in self.base.buscar(pergunta) if pontos >= 3]
            if resultados:
                orientacao, fim = self._exibir_resultados(resultados[:3])
                break

            print("Não encontrei uma orientação. Você pode reformular ou navegar pelas categorias.")
            print("1. Reformular | 2. Navegar por categorias | 0. Voltar ao menu")
            opcao = ler_opcao(2)
            if opcao == 1:
                continue
            orientacao = self._selecionar_orientacao() if opcao == 2 else None
            if orientacao is not None:
                tentativas += 1
                orientacao.exibir()
            fim = time.time()
            break

        ajudou = self._feedback() if orientacao is not None else None
        self.registrar("pergunta", pergunta, orientacao, ajudou, tentativas, fim - inicio)

    @staticmethod
    def _exibir_resultados(resultados):
        pontos, melhor = resultados[0]
        nivel = "alta" if pontos >= 6 else "média"
        print(f"Confiança da busca: {nivel} ({pontos} pontos)")
        melhor.exibir()
        fim = time.time()
        alternativas = resultados[1:]
        if alternativas:
            print("\nOutras orientações relacionadas")
            for numero, (pontos, orientacao) in enumerate(alternativas, start=1):
                print(f"{numero}. {orientacao.titulo} ({pontos} pontos)")
            print("0. Voltar para a orientação exibida")
            escolha = ler_opcao(len(alternativas))
            if escolha:
                pontos, orientacao = alternativas[escolha - 1]
                nivel = "alta" if pontos >= 6 else "média"
                print(f"Confiança da busca: {nivel} ({pontos} pontos)")
                orientacao.exibir()
                return orientacao, time.time()
        return melhor, fim

    def navegar(self):
        inicio = time.time()
        orientacao = self._selecionar_orientacao()
        if orientacao is not None:
            orientacao.exibir()
            tempo = time.time() - inicio
            self.registrar("categoria", "", orientacao, self._feedback(), 1, tempo)

    def registrar(self, origem, pergunta, orientacao, ajudou, tentativas, tempo):
        if contem_dado_pessoal(pergunta):
            return
        self.historico.append({
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "orientacao_id": orientacao.id if orientacao is not None else None,
            "encontrou": orientacao is not None,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(max(0.0, tempo), 1),
        })
        self._salvar_historico()

    def registrar_facilidade(self, nota):
        self.notas_facilidade.append(nota)
        self._salvar_historico()

    def indicadores(self):
        total = len(self.historico)
        encontrados = [a for a in self.historico if a["encontrou"]]
        avaliados = [a for a in encontrados if a["ajudou"] is not None]
        return {
            "total": total,
            "percentual_encontrado": 100 * len(encontrados) / total if total else None,
            "percentual_ajudou": 100 * sum(a["ajudou"] for a in avaliados) / len(avaliados) if avaliados else None,
            "tempo_medio": sum(a["tempo_segundos"] for a in encontrados) / len(encontrados) if encontrados else None,
            "tentativas_media": sum(a["tentativas"] for a in self.historico) / total if total else None,
            "facilidade_media": sum(self.notas_facilidade) / len(self.notas_facilidade) if self.notas_facilidade else None,
            "sem_solucao": [a for a in self.historico if not a["encontrou"] or a["ajudou"] is False],
        }

    def exibir_indicadores(self):
        dados = self.indicadores()
        print(f"\nAtendimentos: {dados['total']}")
        for chave, rotulo, unidade in (
            ("percentual_encontrado", "Respostas encontradas", "%"),
            ("percentual_ajudou", "Respostas que ajudaram entre as avaliadas", "%"),
            ("tempo_medio", "Tempo médio para encontrar", " s"),
            ("tentativas_media", "Tentativas por atendimento", ""),
            ("facilidade_media", "Facilidade média", "/5"),
        ):
            valor = dados[chave]
            medida = f"{valor:.1f}{unidade}" if valor is not None else "sem dados"
            print(f"{rotulo}: {medida}")
        sem_solucao = dados["sem_solucao"]
        print(f"Dúvidas sem solução: {len(sem_solucao)}")
        for atendimento in sem_solucao:
            texto = atendimento["pergunta"] or f"Orientação {atendimento['orientacao_id']}"
            print(f"- {texto}")
        print("0. Voltar ao menu")
        ler_opcao(0)

    def exportar_csv(self, caminho):
        caminho = Path(caminho)
        try:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    linha = atendimento.copy()
                    # Campos de texto são abertos em planilhas como texto literal.
                    for campo in ("pergunta", "orientacao_id", "data"):
                        valor = linha[campo]
                        if valor and valor.lstrip().startswith(("=", "+", "-", "@")):
                            linha[campo] = "'" + valor
                    escritor.writerow(linha)
            print(f"CSV exportado para {caminho}")
        except OSError:
            print("Não foi possível exportar o CSV. Verifique se o arquivo está aberto.")

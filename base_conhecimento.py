import json
import unicodedata
from pathlib import Path

from orientacao import Orientacao


def normalizar(texto):
    decomposicao = unicodedata.normalize("NFD", texto.lower())
    sem_acentos = "".join(c for c in decomposicao if not unicodedata.combining(c))
    sem_pontuacao = "".join(c if c.isalnum() else " " for c in sem_acentos)
    return " ".join(sem_pontuacao.split())


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []
        self.carregar()

    def carregar(self):
        self.orientacoes = []
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8-sig"))
            if not isinstance(dados, list):
                raise ValueError("a base deve ser uma lista")
            orientacoes = []
            ids = set()
            for item in dados:
                orientacao = Orientacao(**item)
                for campo in ("id", "categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
                    valor = getattr(orientacao, campo)
                    if not isinstance(valor, str) or not valor.strip():
                        raise ValueError(f"campo inválido: {campo}")
                for lista, minimo in ((orientacao.palavras_chave, 3), (orientacao.documentos, 0)):
                    if not isinstance(lista, list) or len(lista) < minimo:
                        raise ValueError("lista de palavras-chave ou documentos inválida")
                    if any(not isinstance(s, str) or not s.strip() for s in lista):
                        raise ValueError("palavra-chave ou documento inválido")
                if orientacao.id in ids:
                    raise ValueError("ID de orientação duplicado")
                ids.add(orientacao.id)
                orientacoes.append(orientacao)
            self.orientacoes = orientacoes
        except (OSError, ValueError, TypeError) as erro:
            print(f"Base de conhecimento indisponível ({self.caminho.name}): {erro}.")

    def categorias(self):
        return list(dict.fromkeys(o.categoria for o in self.orientacoes))

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta = normalizar(pergunta)
        palavras_titulo = set(normalizar(orientacao.titulo).split())
        palavras_chave = set(map(normalizar, orientacao.palavras_chave))
        # Os espaços permitem conferir termos completos, inclusive expressões.
        pergunta_com_limites = f" {pergunta} "
        pontos_chave = sum(
            3 for chave in palavras_chave if chave and f" {chave} " in pergunta_com_limites
        )
        pontos_titulo = sum(
            1 for palavra in set(pergunta.split()) if len(palavra) >= 4 and palavra in palavras_titulo
        )
        return pontos_chave + pontos_titulo

    def buscar(self, pergunta):
        resultados = [(self.pontuar(pergunta, o), o) for o in self.orientacoes]
        return sorted(resultados, key=lambda resultado: resultado[0], reverse=True)

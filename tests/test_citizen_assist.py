import csv
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from assistente import Assistente, CAMPOS_CSV
from base_conhecimento import BaseConhecimento, normalizar
from main import main
from orientacao import Orientacao


BASE_ORIGINAL = Path(__file__).resolve().parents[1] / "data" / "base_conhecimento.json"


class TestCitizenAssist(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.dados = Path(temporario.name)
        self.caminho_base = self.dados / "base_conhecimento.json"
        self.caminho_historico = self.dados / "historico.json"
        shutil.copyfile(BASE_ORIGINAL, self.caminho_base)
        self.base = BaseConhecimento(self.caminho_base)
        self.assistente = Assistente("Citizen Assist AI", self.base, self.caminho_historico)

    def executar(self, funcao, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas) as teclado, redirect_stdout(saida):
            funcao()
        self.assertEqual(teclado.call_count, len(entradas))
        return saida.getvalue()

    def test_base_entregue(self):
        self.assertEqual(len(self.base.categorias()), 3)
        self.assertGreaterEqual(len(self.base.orientacoes), 10)
        exemplos = {
            "Como fazer o primeiro Cartão SUS?": "cns-01",
            "Onde vejo o número do CNS?": "cns-02",
            "Como tirar a segunda via do cartão SUS?": "cns-03",
            "Como atualizar cadastro?": "cns-04",
            "Onde tomar vacina?": "vac-01",
            "Quero consultar vacinas no aplicativo": "vac-02",
            "Minha vacina não aparece no aplicativo": "vac-03",
            "Onde tem o calendário de vacinação?": "vac-04",
            "Como localizar UBS perto de casa?": "ubs-01",
            "A UBS faz consulta de rotina?": "ubs-02",
            "Tem como agendar consulta?": "ubs-03",
            "Posso ser atendido sem cartão SUS?": "ubs-04",
        }
        for pergunta, esperado in exemplos.items():
            with self.subTest(pergunta=pergunta):
                pontos, orientacao = self.base.buscar(pergunta)[0]
                self.assertGreaterEqual(pontos, 3)
                self.assertEqual(orientacao.id, esperado)

    def test_normaliza_e_pontua_termos_inteiros(self):
        orientacao = Orientacao(
            "teste", "Teste", "Cartão Digital do SUS",
            ["Cartão-SUS", "digital", "UBS"], "", [], "", "", "",
        )
        self.assertEqual(normalizar("  CartÃO-SUS, digital! "), "cartao sus digital")
        self.assertEqual(self.base.pontuar("Cartão-SUS digital digital", orientacao), 8)
        self.assertEqual(self.base.pontuar("subsolo cartões", orientacao), 0)
        pontos = [p for p, _ in self.base.buscar("primeiro cartão SUS")]
        self.assertEqual(pontos, sorted(pontos, reverse=True))

    def test_base_ausente_e_corrompida(self):
        self.caminho_base.unlink()
        self.assertIn("indisponível", self.executar(self.base.carregar, []))
        self.assertEqual(self.base.buscar("cartão"), [])
        for conteudo in ("{", "[42]", "[{}]", '{"orientacoes": []}'):
            with self.subTest(conteudo=conteudo):
                self.caminho_base.write_text(conteudo, encoding="utf-8")
                saida = self.executar(lambda: main(self.dados), ["1", "2", "0", "4"])
                self.assertIn("Base de conhecimento indisponível", saida)
                self.assertIn("Nenhuma orientação disponível", saida)
                self.assertIn("Nenhuma categoria disponível", saida)

    def test_bloqueia_dados_antes_de_buscar_e_gravar(self):
        entradas = ["exemplo@teste", "1 2 3 4 5 6 7 8", "١٢٣٤٥٦٧٨", "", "0"]
        with patch.object(self.base, "buscar") as buscar:
            saida = self.executar(self.assistente.perguntar, entradas)
        self.assertEqual(saida.count("Pergunta recusada"), 3)
        buscar.assert_not_called()

        self.assistente.registrar("pergunta", "a@b", None, None, 1, 1)
        self.assertEqual(self.assistente.historico, [])
        self.assertFalse(self.caminho_historico.exists())

    def test_busca_reformula_e_valida_feedback(self):
        with patch("assistente.time.time", side_effect=[100, 108.26]):
            saida = self.executar(self.assistente.perguntar, [
                "astronomia", "9", "1", "Como atualizar cadastro? Mudei de endereço.", "", "sim", "S",
            ])
        self.assertIn("reformular", saida)
        self.assertIn("Confiança da busca: alta", saida)
        for campo in ("Documentos:", "Onde:", "Fonte oficial:", "Verificado em:", "canal oficial"):
            self.assertIn(campo, saida)
        self.assertEqual(saida.count("Resposta inválida"), 2)
        registro, = self.assistente.historico
        self.assertTrue(registro["ajudou"])
        self.assertEqual(registro["tentativas"], 2)
        self.assertEqual(registro["tempo_segundos"], 8.3)
        self.assertEqual(registro["orientacao_id"], "cns-04")

    def test_busca_sem_solucao(self):
        self.executar(self.assistente.perguntar, ["astronomia", "1", "xilofone", "0"])
        registro, = self.assistente.historico
        self.assertEqual(registro["pergunta"], "xilofone")
        self.assertFalse(registro["encontrou"])
        self.assertIsNone(registro["ajudou"])
        self.assertEqual(registro["tentativas"], 2)

    def test_navegacao_e_retorno(self):
        saida = self.executar(self.assistente.navegar, ["", "x", "99", "1", "0", "2", "2", "n"])
        self.assertEqual(saida.count("Opção inválida"), 3)
        self.assertIn("Consultar a carteira digital de vacinação", saida)
        registro, = self.assistente.historico
        self.assertEqual(registro["origem"], "categoria")
        self.assertEqual(registro["pergunta"], "")
        self.assertEqual(registro["orientacao_id"], "vac-02")
        self.assertFalse(registro["ajudou"])

    def test_navegacao_apos_busca_sem_resultado(self):
        self.executar(self.assistente.perguntar, ["xilofone", "2", "3", "3", "0"])
        registro, = self.assistente.historico
        self.assertEqual(registro["origem"], "pergunta")
        self.assertEqual(registro["tentativas"], 2)
        self.assertEqual(registro["orientacao_id"], "ubs-03")
        self.assertIsNone(registro["ajudou"])

    def test_alternativas_limitadas_e_selecao(self):
        orientacoes = self.base.orientacoes[:4]
        resultados = list(zip([7, 5, 3, 3], orientacoes))
        with patch.object(self.base, "buscar", return_value=resultados):
            saida = self.executar(self.assistente.perguntar, ["cartão", "2", "s"])
        self.assertIn("Confiança da busca: alta (7 pontos)", saida)
        self.assertIn("Confiança da busca: média (3 pontos)", saida)
        self.assertNotIn(orientacoes[3].titulo, saida)
        self.assertEqual(self.assistente.historico[0]["orientacao_id"], orientacoes[2].id)

    def test_historico_indicadores_e_csv(self):
        orientacao = self.base.orientacoes[0]
        self.assistente.registrar("pergunta", "Cartão, como faço?", orientacao, True, 1, 3)
        self.assistente.registrar("categoria", "", orientacao, False, 1, 5)
        self.assistente.registrar("pergunta", "=texto", None, None, 3, 16)
        self.assistente.registrar("categoria", "", orientacao, None, 1, 4)
        self.assistente.registrar_facilidade(3)
        self.assistente.registrar_facilidade(4)

        recarregado = Assistente("Teste", self.base, self.caminho_historico)
        indicadores = recarregado.indicadores()
        self.assertEqual(indicadores["percentual_encontrado"], 75)
        self.assertEqual(indicadores["percentual_ajudou"], 50)
        self.assertEqual(indicadores["tempo_medio"], 4)
        self.assertEqual(indicadores["tentativas_media"], 1.5)
        self.assertEqual(indicadores["facilidade_media"], 3.5)
        self.assertEqual(len(indicadores["sem_solucao"]), 2)
        csv_path = self.dados / "atendimentos.csv"
        self.executar(lambda: recarregado.exportar_csv(csv_path), [])
        with csv_path.open(encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            linhas = list(leitor)
        self.assertEqual(tuple(leitor.fieldnames), CAMPOS_CSV)
        self.assertEqual(len(linhas), 4)
        self.assertEqual(linhas[0]["pergunta"], "Cartão, como faço?")
        self.assertEqual(linhas[2]["pergunta"], "'=texto")

    def test_historico_corrompido_preservado(self):
        for conteudo in ("{", '["registro inválido"]'):
            with self.subTest(conteudo=conteudo):
                self.caminho_historico.write_text(conteudo, encoding="utf-8")
                saida = self.executar(lambda: main(self.dados), ["2", "1", "1", "s", "0", "5"])
                self.assertIn("Histórico indisponível", saida)
                self.assertIn("Obrigado", saida)
                self.assertEqual(self.caminho_historico.read_text(encoding="utf-8"), conteudo)

    def test_menu_e_nota_de_saida(self):
        self.caminho_historico.write_text("[]", encoding="utf-8")
        saida = self.executar(lambda: main(self.dados), ["", "x", "9", "3", "0", "0", "0", "0", "6", "5"])
        self.assertEqual(saida.count("Opção inválida"), 4)
        self.assertIn("Facilidade média: sem dados", saida)
        dados = json.loads(self.caminho_historico.read_text(encoding="utf-8"))
        self.assertEqual(dados, {"atendimentos": [], "notas_facilidade": [5]})


if __name__ == "__main__":
    unittest.main()

"""Executa dez casos roteirizados em três processos reais de terminal."""

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJETO = Path(__file__).resolve().parents[1]
SESSOES = (
    (
        [
            "1", "Como faço o cartão do SUS?", "s",
            "1", "Onde vejo o número do CNS?", "s",
            "1", "Preciso mudar uma informação", "1", "Mudei de endereço", "s",
            "2", "2", "1", "s",
            "0", "4",
        ],
        ["cns-01", "cns-02", "cns-04", "vac-01"],
        4,
    ),
    (
        [
            "1", "Minha vacina não aparece no aplicativo", "s",
            "1", "Onde tem o calendário de vacinação?", "s",
            "1", "Como localizar UBS perto de casa?", "s",
            "0", "5",
        ],
        ["vac-03", "vac-04", "ubs-01"],
        5,
    ),
    (
        [
            "1", "Tem como agendar consulta?", "s",
            "2", "3", "4", "s",
            "1", "Como transferir meu título de eleitor?", "0",
            "4", "0", "4",
        ],
        ["ubs-03", "ubs-04", None],
        4,
    ),
)


def simular(destino):
    with tempfile.TemporaryDirectory() as pasta_temporaria:
        pasta = Path(pasta_temporaria)
        for nome in ("main.py", "assistente.py", "base_conhecimento.py", "orientacao.py"):
            shutil.copyfile(PROJETO / nome, pasta / nome)
        dados = pasta / "data"
        dados.mkdir()
        shutil.copyfile(PROJETO / "data" / "base_conhecimento.json", dados / "base_conhecimento.json")

        ids_previstos = []
        notas_previstas = []
        for numero, (entradas, ids, nota) in enumerate(SESSOES, start=1):
            processo = subprocess.run(
                [sys.executable, "-X", "utf8", str(pasta / "main.py")],
                input="\n".join(entradas) + "\n",
                encoding="utf-8",
                capture_output=True,
                timeout=15,
                check=False,
            )
            if processo.returncode or "Obrigado por usar o assistente." not in processo.stdout:
                raise RuntimeError(f"Sessão simulada {numero} não terminou como previsto.\n{processo.stdout}\n{processo.stderr}")

            ids_previstos.extend(ids)
            notas_previstas.append(nota)
            historico = json.loads((dados / "historico.json").read_text(encoding="utf-8"))
            ids_obtidos = [linha["orientacao_id"] for linha in historico["atendimentos"]]
            if ids_obtidos != ids_previstos or historico["notas_facilidade"] != notas_previstas:
                raise RuntimeError(f"Os registros da sessão simulada {numero} divergiram do roteiro.")
            print(f"Sessão simulada {numero} concluída com {len(ids)} atendimentos.")

        with (dados / "atendimentos.csv").open(encoding="utf-8-sig", newline="") as arquivo:
            exportados = [linha["orientacao_id"] or None for linha in csv.DictReader(arquivo)]
        if exportados != ids_previstos:
            raise RuntimeError("O CSV exportado divergiu do histórico.")

        destino.mkdir(parents=True, exist_ok=True)
        for nome in ("historico.json", "atendimentos.csv"):
            shutil.copyfile(dados / nome, destino / nome)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path, help="Pasta para gravar a evidência simulada")
    simular(parser.parse_args().destino)

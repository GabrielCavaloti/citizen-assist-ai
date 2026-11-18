"""Interface local do módulo de energia. Execute com python energia_web.py."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from energia import DADOS, calcular, responder

WEB = Path(__file__).resolve().parent / "web"
ROTAS = {"/": ("index.html", "text/html"), "/estilos.css": ("estilos.css", "text/css"),
         "/simulador.js": ("simulador.js", "text/javascript")}


class InterfaceEnergia(BaseHTTPRequestHandler):
    def enviar(self, status, conteudo, tipo):
        self.send_response(status)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    def enviar_json(self, status, dados):
        self.enviar(status, json.dumps(dados, ensure_ascii=False).encode("utf-8"), "application/json")

    def do_GET(self):
        if self.path == "/api/referencia":
            self.enviar_json(200, {"resultado": calcular(), "fontes": DADOS["fontes"]})
        elif self.path in ROTAS:
            nome, tipo = ROTAS[self.path]
            self.enviar(200, (WEB / nome).read_bytes(), tipo)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/energia":
            self.send_error(404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 4096:
                raise ValueError("O tamanho da solicitação é inválido.")
            dados = json.loads(self.rfile.read(tamanho))
            if not isinstance(dados, dict):
                raise ValueError("Preencha os campos do simulador.")
            pergunta = dados.get("pergunta", "")
            if not isinstance(pergunta, str) or len(pergunta) > 240:
                raise ValueError("Use até 240 caracteres na pergunta.")
            resultado = calcular(dados.get("lampadas"), dados.get("horas"),
                                 dados.get("tarifa"), dados.get("cenario"))
        except ValueError as erro:
            mensagem = "Preencha os campos do simulador." if isinstance(erro, (json.JSONDecodeError, UnicodeError)) else str(erro)
            self.enviar_json(400, {"erro": mensagem})
            return
        self.enviar_json(200, {"resultado": resultado, "resposta": responder(pergunta, resultado)})


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--porta", type=int, default=8765)
    opcoes = argumentos.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", opcoes.porta), InterfaceEnergia) as servidor:
        print(f"Abra http://127.0.0.1:{opcoes.porta}", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass

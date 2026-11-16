from dataclasses import dataclass


@dataclass
class Orientacao:
    id: str
    categoria: str
    titulo: str
    palavras_chave: list[str]
    resposta: str
    documentos: list[str]
    onde: str
    fonte: str
    verificado_em: str

    def exibir(self):
        print(f"\n{self.titulo}")
        print(self.resposta)
        print("Documentos:", " | ".join(self.documentos) or "Nenhum para consultar.")
        print(f"Onde: {self.onde}")
        print(f"Fonte oficial: {self.fonte}")
        print(f"Verificado em: {self.verificado_em}")
        print("O Citizen Assist AI é um projeto acadêmico e não é um canal oficial do SUS.")

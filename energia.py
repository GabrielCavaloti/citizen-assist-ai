"""Análise de iluminação residencial usada pelo terminal e pelo simulador web."""
import json
import math
import re
import unicodedata
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP


DADOS = json.loads((Path(__file__).resolve().parent / "data" / "energia.json").read_text(encoding="utf-8"))
REFERENCIA = DADOS["referencia"]
SOLAR = DADOS["solar"]
CENARIOS = {"junho": SOLAR["irradiacao"][SOLAR["mes_referencia"]], "pouco_sol": SOLAR["hsp_estresse"]}


def br(valor, casas=2):
    arredondado = Decimal(str(valor)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    return f"{arredondado:,.{casas}f}".translate(str.maketrans(".,", ",."))


def numero(valor, rotulo, minimo, maximo):
    try:
        resultado = float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        resultado = math.nan
    if not math.isfinite(resultado) or not minimo <= resultado <= maximo:
        raise ValueError(f"Informe {rotulo} entre {br(minimo)} e {br(maximo)}.")
    return resultado


def calcular(lampadas=REFERENCIA["lampadas"], horas=REFERENCIA["horas_dia"],
             tarifa=REFERENCIA["tarifa"], cenario="junho"):
    quantidade = numero(lampadas, "a quantidade de lâmpadas", 1, 30)
    if not quantidade.is_integer():
        raise ValueError("Informe uma quantidade inteira de lâmpadas.")
    quantidade = int(quantidade)
    horas = numero(horas, "as horas de uso por dia", 0, 24)
    tarifa = numero(tarifa, "o valor variável em R$/kWh", 0, 5)
    if not isinstance(cenario, str) or cenario not in CENARIOS:
        raise ValueError("Selecione um cenário de irradiação.")
    dias = REFERENCIA["dias"]
    potencia_base = quantidade * REFERENCIA["watts_incandescente"]
    potencia_led = quantidade * REFERENCIA["watts_led"]
    base = potencia_base * horas * dias / 1000
    led = potencia_led * horas * dias / 1000
    carga_diaria = led / dias

    energia_dc = SOLAR["kwp"] * CENARIOS[cenario] * SOLAR["rendimento_carga"]
    inversor = SOLAR["rendimento_inversor"]
    auxiliar = SOLAR["consumo_auxiliar_kwh_dia"]
    bateria_util = SOLAR["bateria_v"] * SOLAR["bateria_ah"] * SOLAR["fracao_util_bateria"] / 1000
    diaria_bateria = carga_diaria / inversor + auxiliar
    energia_solar_diaria = min(carga_diaria, max(0, min(bateria_util, energia_dc) - auxiliar) * inversor)
    solar_usada = round(energia_solar_diaria * dias, 12)
    solar_rede = max(0, round(led - solar_usada, 12))

    orcamento = DADOS["orcamento_ilustrativo"]
    investimento_led = quantidade * orcamento["led_unitario"]
    adicional_solar = sum(orcamento["solar"].values())
    fator = DADOS["fator_sin_kg_co2_kwh"]
    retorno_led = investimento_led / ((base - led) * tarifa) if base > led and tarifa else None
    retorno_solar = adicional_solar / (solar_usada * tarifa) if solar_usada and tarifa else None
    return {
        "quantidade": quantidade, "horas": horas, "tarifa": tarifa, "dias": dias,
        "hsp": CENARIOS[cenario], "potencia_base": potencia_base, "potencia_led": potencia_led,
        "energia_dc_dia": energia_dc, "bateria_util": bateria_util, "carga_dia": carga_diaria,
        "autonomia_dias": bateria_util / diaria_bateria if carga_diaria else None,
        "economia_led_kwh": base - led,
        "cobertura_pct": 100 * solar_usada / led if led else None,
        "retorno_led": retorno_led, "retorno_solar": retorno_solar,
        "opcoes": [
            {"nome": "Incandescente + rede", "consumo": base, "rede": base, "solar": 0,
             "custo": base * tarifa, "investimento": 0, "co2": base * fator},
            {"nome": "LED + rede", "consumo": led, "rede": led, "solar": 0,
             "custo": led * tarifa, "investimento": investimento_led, "co2": led * fator},
            {"nome": "LED + solar com bateria", "consumo": led, "rede": solar_rede, "solar": solar_usada,
             "custo": solar_rede * tarifa, "investimento": investimento_led + adicional_solar,
             "co2": solar_rede * fator},
        ],
    }


def responder(pergunta, resultado):
    texto = unicodedata.normalize("NFKD", pergunta.casefold())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    palavras = set(re.findall(r"[a-z]+", texto))
    base, led, solar = resultado["opcoes"]
    if not palavras:
        return "Escreva uma pergunta sobre iluminação, custos, energia solar ou impacto ambiental."
    if palavras & {"ambiental", "impacto", "emissao", "emissoes", "carbono", "co"}:
        return (f"No cenário, a rede associada à iluminação representa {br(base['co2'])} kg de CO₂ "
                f"na referência, {br(led['co2'])} kg com LED e {br(solar['co2'])} kg com solar. "
                "É um indicador operacional com o fator médio do SIN de 2023. Fabricação, transporte e descarte "
                "de lâmpadas, painel, inversor e bateria ficam fora dessa conta.")
    if palavras & {"solar", "painel", "bateria", "chuva", "nublado", "sol", "autonomia", "fotovoltaica"}:
        if resultado["cobertura_pct"] is None:
            return "O uso informado é zero. Ligue a simulação a uma necessidade de iluminação maior que zero para avaliar o kit solar."
        return (f"Com {br(resultado['hsp'])} horas de sol pico no cenário, o modelo estima "
                f"{br(solar['solar'])} kWh solares usados em {resultado['dias']} dias e "
                f"{br(solar['rede'])} kWh da rede como complemento. Uma bateria cheia tem autonomia nominal de "
                f"{br(resultado['autonomia_dias'], 1)} dia(s) nesse uso. O kit opera separado da rede. "
                "Sombra e dias nublados consecutivos podem reduzir a cobertura. Para manter a iluminação, "
                "preveja alimentação de reserva projetada por profissional.")
    if palavras & {"consumo", "consome", "potencia", "calcular", "calculo", "kwh", "watt", "watts"}:
        return (f"A potência total passa de {resultado['potencia_base']} W para {resultado['potencia_led']} W. "
                f"Multiplicamos a potência em kW por {br(resultado['horas'])} hora(s) diárias e "
                f"{resultado['dias']} dias. O consumo cai de {br(base['consumo'])} para {br(led['consumo'])} kWh "
                "com lâmpadas de aproximadamente 800 lúmens por ponto.")
    if palavras & {"led", "economia", "economizar", "custo", "custos", "pagar", "gasto", "gastar", "conta", "recomenda", "recomendacao", "vale", "comparar", "melhor", "iluminacao", "lampada", "lampadas", "troco", "trocar"}:
        if not resultado["economia_led_kwh"]:
            return "Com zero horas de uso, o cenário não apresenta consumo nem economia de iluminação."
        economia = base["custo"] - led["custo"]
        retorno = resultado["retorno_led"]
        prazo = f" O retorno simples é de cerca de {br(retorno, 1)} meses." if retorno is not None else ""
        return (f"Comece pelo LED de aproximadamente 800 lúmens se ainda usa incandescentes de 60 W. "
                f"A economia estimada é de {br(resultado['economia_led_kwh'])} kWh e R$ {br(economia)} em "
                f"{resultado['dias']} dias, com compra ilustrativa de R$ {br(led['investimento'])}.{prazo} "
                "Confira lúmens, encaixe, tensão e o preço do kWh variável na sua conta. "
                "Avalie solar com bateria se a autonomia tiver valor para a família e houver local e orçamento viáveis.")
    return ("Posso orientar sobre a iluminação deste cenário. Experimente “Quanto economizo com LED?”, "
            "“E com pouco sol?” ou “Qual é o impacto ambiental?”.")


def menu_energia():
    print("\nEnergia e sustentabilidade — iluminação residencial")
    print("Referência: lâmpadas antigas de 60 W. Alternativas: LED de 9 W e LED com solar e bateria.")
    try:
        lampadas = input("Número de lâmpadas [6]: ").strip() or "6"
        horas = input("Horas de uso por dia [5]: ").strip() or "5"
        tarifa = input("Preço variável em R$/kWh [1,00]: ").strip() or "1,00"
        escolha = input("Irradiação: 1. Junho em São Paulo  2. Pouco sol [1]: ").strip() or "1"
        cenario = {"1": "junho", "2": "pouco_sol"}.get(escolha)
        resultado = calcular(lampadas, horas, tarifa, cenario)
    except ValueError as erro:
        print(erro)
        return
    print(f"\nComparação para {resultado['dias']} dias, somente iluminação.")
    for opcao in resultado["opcoes"]:
        print(f"- {opcao['nome']}: {br(opcao['consumo'])} kWh de consumo, "
              f"{br(opcao['rede'])} kWh da rede, R$ {br(opcao['custo'])} de energia variável, "
              f"R$ {br(opcao['investimento'])} de investimento ilustrativo e "
              f"{br(opcao['co2'])} kg de CO₂ da rede.")
    print()
    print(responder("Quanto economizo com LED?", resultado))
    print("Pergunte sobre LED, solar, consumo ou impacto ambiental. Enter volta ao menu.")
    while pergunta := input("\nSua pergunta: ").strip():
        print(responder(pergunta, resultado))
        print("Consulte as fontes e premissas em docs/energia.md.")

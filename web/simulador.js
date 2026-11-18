"use strict";

const $ = (id) => document.getElementById(id);
const real = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const decimal = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
const umaCasa = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });
const kwh = (valor) => decimal.format(valor) + " kWh";
const padrao = "Escolha uma pergunta ou escreva a sua. A resposta usa os valores do simulador.";
let requisicaoAtual = 0;

function elemento(tag, texto, classe) {
  const item = document.createElement(tag);
  if (texto) item.textContent = texto;
  if (classe) item.className = classe;
  return item;
}

function mostrar(resultado) {
  const [base, led, solar] = resultado.opcoes;
  const opcoes = resultado.opcoes.map((opcao) => {
    const linha = elemento("article", "", "opcao");
    const cabecalho = elemento("div", "", "opcao-cabecalho");
    cabecalho.append(elemento("h3", opcao.nome), elemento("strong", kwh(opcao.rede) + " da rede"));
    const trilho = elemento("div", "", "trilho");
    trilho.setAttribute("aria-hidden", "true");
    const nivel = elemento("div");
    nivel.style.width = (base.rede ? 100 * opcao.rede / base.rede : 0) + "%";
    trilho.append(nivel);
    linha.append(cabecalho, trilho, elemento("p",
      real.format(opcao.custo) + " de energia variável · " +
      real.format(opcao.investimento) + " de investimento · " +
      decimal.format(opcao.co2) + " kg de CO₂ da rede"));
    return linha;
  });
  $("opcoes").replaceChildren(...opcoes);
  $("economia").textContent = kwh(resultado.economia_led_kwh) + " · " + real.format(base.custo - led.custo);
  $("cobertura").textContent = resultado.cobertura_pct === null
    ? "Sem uso informado"
    : umaCasa.format(resultado.cobertura_pct) + "% · " + kwh(solar.solar);
  $("calculo").textContent = "Potência total em kW × horas diárias × 30 dias. " +
    resultado.potencia_base + " W na referência e " + resultado.potencia_led + " W com LED. " +
    "O custo variável usa " + real.format(resultado.tarifa) + "/kWh.";
  $("retorno").textContent = "Retorno simples ilustrativo: LED em " +
    (resultado.retorno_led === null ? "prazo não calculável" : umaCasa.format(resultado.retorno_led) + " meses") +
    " e investimento solar adicional em " +
    (resultado.retorno_solar === null ? "prazo não calculável" : umaCasa.format(resultado.retorno_solar) + " meses") +
    ". O cálculo exclui manutenção, reposição de bateria e financiamento.";
  $("bateria").textContent = decimal.format(resultado.hsp) + " horas de sol pico no cenário e " +
    kwh(resultado.energia_dc_dia) + " por dia estimados antes do inversor. Bateria de " +
    kwh(resultado.bateria_util) + " úteis antes das perdas do inversor" +
    (resultado.autonomia_dias === null ? "." : ", com autonomia nominal de " +
      umaCasa.format(resultado.autonomia_dias) + " dia(s) neste uso a partir de carga cheia.");
}

async function enviar(pergunta = "") {
  if (!$("cenario").reportValidity()) return;
  const requisicao = ++requisicaoAtual;
  const campos = Object.fromEntries(new FormData($("cenario")));
  $("erro").hidden = true;
  try {
    const resposta = await fetch("/api/energia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...campos, pergunta }),
    });
    const dados = await resposta.json();
    if (requisicao !== requisicaoAtual) return;
    if (!resposta.ok) throw new Error(dados.erro);
    mostrar(dados.resultado);
    $("pergunta-enviada").hidden = !pergunta;
    $("pergunta-enviada").textContent = pergunta;
    $("texto-resposta").textContent = pergunta ? dados.resposta : padrao;
  } catch (erro) {
    if (requisicao !== requisicaoAtual) return;
    $("erro").textContent = erro.message === "Failed to fetch"
      ? "Confira se o servidor do simulador está aberto." : erro.message;
    $("erro").hidden = false;
    if (pergunta) $("erro").scrollIntoView({ block: "nearest" });
  }
}

$("cenario").addEventListener("submit", (evento) => {
  evento.preventDefault();
  enviar();
});
$("conversa").addEventListener("submit", (evento) => {
  evento.preventDefault();
  enviar($("pergunta").value.trim());
});
document.querySelectorAll("[data-pergunta]").forEach((botao) => {
  botao.addEventListener("click", () => {
    $("pergunta").value = "";
    enviar(botao.dataset.pergunta);
  });
});

fetch("/api/referencia").then((resposta) => {
  if (!resposta.ok) throw new Error();
  return resposta.json();
}).then(({ resultado, fontes }) => {
  if (!requisicaoAtual) mostrar(resultado);
  $("links").replaceChildren(...fontes.map(({ nome, url }) => {
    const item = elemento("li");
    const link = elemento("a", nome);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    item.append(link);
    return item;
  }));
}).catch(() => {
  $("erro").textContent = "Não foi possível carregar o cenário. Reabra o servidor e recarregue a página.";
  $("erro").hidden = false;
});

import unittest

from energia import calcular, responder


class TestEnergia(unittest.TestCase):
    def test_referencia_e_orcamento(self):
        resultado = calcular()
        base, led, solar = resultado["opcoes"]
        self.assertEqual(base["consumo"], 54)
        self.assertEqual(led["consumo"], 8.1)
        self.assertAlmostEqual(led["co2"], 0.31185)
        self.assertEqual(solar["investimento"], 2072)
        self.assertEqual(solar["rede"], 0)
        self.assertAlmostEqual(resultado["retorno_led"], 72 / 45.9)
        self.assertAlmostEqual(resultado["autonomia_dias"], 512 / 310)

    def test_pouco_sol_e_complemento(self):
        resultado = calcular(cenario="pouco_sol")
        solar = resultado["opcoes"][2]
        self.assertAlmostEqual(solar["solar"], 5.805)
        self.assertAlmostEqual(solar["rede"], 2.295)
        self.assertIn("2,30 kWh da rede", responder("E com pouco sol?", resultado))

    def test_tarifa_editavel_e_resposta_consistente(self):
        resultado = calcular(tarifa="0,85")
        self.assertIn("R$ 39,02", responder("Quanto economizo com LED?", resultado))
        self.assertIn("54,00 para 8,10 kWh", responder("Como calculou o consumo?", resultado))

    def test_zero_uso_ou_tarifa(self):
        sem_uso = calcular(horas=0)
        self.assertIsNone(sem_uso["cobertura_pct"])
        self.assertEqual(sem_uso["opcoes"][2]["solar"], 0)
        self.assertIsNone(calcular(tarifa=0)["retorno_led"])
        self.assertIsNone(calcular(tarifa=0)["retorno_solar"])

    def test_entradas_invalidas(self):
        for campos in ({"lampadas": 0}, {"lampadas": 1.5}, {"horas": 25},
                       {"tarifa": "nan"}, {"tarifa": -1}, {"cenario": "inexistente"},
                       {"cenario": []}):
            with self.subTest(campos=campos), self.assertRaises(ValueError):
                calcular(**campos)

    def test_pergunta_fora_do_escopo(self):
        self.assertIn("iluminação", responder("Qual ônibus vai ao centro?", calcular()))

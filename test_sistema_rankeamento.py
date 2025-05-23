import unittest
import tkinter as tk
from ranker import Ranker as Rankeador  # Supondo que a classe principal seja Rankeador

class TestSistemaDeRankeamento(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.items = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador = Rankeador(self.root, self.frame, self.items)

    # Testes Unitários

    def test_TU01_botao_iniciar_habilitado(self):
        """Selecionar 3 jogos e verificar se o botão está habilitado"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador.selecionar_jogos(jogos)
        self.assertTrue(self.rankeador.botao_iniciar_habilitado())

    def test_TU02_botao_iniciar_desabilitado_com_um_jogo(self):
        """Selecionar 1 jogo e verificar se o botão permanece desabilitado"""
        jogos = ['Jogo A']
        self.rankeador.selecionar_jogos(jogos)
        self.assertFalse(self.rankeador.botao_iniciar_habilitado())

    def test_TU03_contabilizar_voto(self):
        """Votar em um jogo e verificar se o voto foi registrado"""
        jogos = ['Jogo A', 'Jogo B']
        self.rankeador.selecionar_jogos(jogos)
        self.rankeador.votar('Jogo A')
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 1)
        self.assertEqual(resultado['Jogo B'], 0)

    def test_TU04_registrar_empate(self):
        """Clicar em empate e verificar se nenhum ponto foi atribuído"""
        jogos = ['Jogo A', 'Jogo B']
        self.rankeador.selecionar_jogos(jogos)
        self.rankeador.empatar()
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 0)
        self.assertEqual(resultado['Jogo B'], 0)

    def test_TU05_funcao_voltar(self):
        """Avançar, voltar e verificar se índice retorna e voto é removido"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador.selecionar_jogos(jogos)
        self.rankeador.votar('Jogo A')
        self.rankeador.votar('Jogo B')
        self.rankeador.voltar()
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 1)
        self.assertEqual(resultado['Jogo B'], 0)

    # Testes de Integração

    def test_TI01_fluxo_valido_com_4_jogos(self):
        """Selecionar 4 jogos, votar sempre na primeira opção e verificar ranking final"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C', 'Jogo D']
        self.rankeador.selecionar_jogos(jogos)
        while not self.rankeador.fim():
            par = self.rankeador.obter_par_atual()
            self.rankeador.votar(par[0])
        resultado = self.rankeador.obter_resultado()
        self.assertTrue(resultado['Jogo A'] >= resultado['Jogo B'])
        self.assertTrue(resultado['Jogo B'] >= resultado['Jogo C'])
        self.assertTrue(resultado['Jogo C'] >= resultado['Jogo D'])

    def test_TI02_fluxo_com_empates(self):
        """Selecionar 3 jogos, empatar todas as comparações e verificar ranking"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador.selecionar_jogos(jogos)
        while not self.rankeador.fim():
            self.rankeador.empatar()
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 0)
        self.assertEqual(resultado['Jogo B'], 0)
        self.assertEqual(resultado['Jogo C'], 0)

    def test_TI03_voltar_e_revotar(self):
        """Votar, voltar e revotar, verificando se ranking é atualizado"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador.selecionar_jogos(jogos)
        self.rankeador.votar('Jogo A')
        self.rankeador.votar('Jogo B')
        self.rankeador.voltar()
        self.rankeador.votar('Jogo C')
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 1)
        self.assertEqual(resultado['Jogo B'], 0)
        self.assertEqual(resultado['Jogo C'], 1)

    def test_TI04_alerta_selecao_invalida(self):
        """Selecionar 0 jogos e verificar se alerta de erro é exibido"""
        jogos = []
        with self.assertRaises(ValueError):
            self.rankeador.selecionar_jogos(jogos)

    # Testes Mestre (End-to-End)

    def test_TM01_ciclo_completo_ranqueamento(self):
        """Executar processo completo de seleção, votação e exibição de ranking"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C', 'Jogo D']
        self.rankeador.selecionar_jogos(jogos)
        while not self.rankeador.fim():
            par = self.rankeador.obter_par_atual()
            self.rankeador.votar(par[0])
        ranking = self.rankeador.exibir_ranking()
        self.assertIsInstance(ranking, list)
        self.assertEqual(len(ranking), 4)

    def test_TM02_responsividade(self):
        """Testar layout com nomes grandes e redimensionamento de tela"""
        jogos = ['Jogo com nome extremamente longo A', 'Jogo com nome extremamente longo B']
        self.rankeador.selecionar_jogos(jogos)
        # Este teste é mais visual; verificar se a interface suporta nomes longos
        # Pode ser necessário implementar verificações específicas na interface gráfica

    def test_TM03_fluxo_completo_com_interacoes(self):
        """Executar todas as interações possíveis: voto, empate, voltar"""
        jogos = ['Jogo A', 'Jogo B', 'Jogo C']
        self.rankeador.selecionar_jogos(jogos)
        self.rankeador.votar('Jogo A')
        self.rankeador.empatar()
        self.rankeador.voltar()
        self.rankeador.votar('Jogo B')
        resultado = self.rankeador.obter_resultado()
        self.assertEqual(resultado['Jogo A'], 1)
        self.assertEqual(resultado['Jogo B'], 1)
        self.assertEqual(resultado['Jogo C'], 0)

if __name__ == '__main__':
    unittest.main()

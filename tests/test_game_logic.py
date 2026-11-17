import pytest
from game_logic import calcular_progressao, xp_para_proximo_nivel

@pytest.mark.parametrize("nivel,exp,ganho,esperado", [
    (5, 120, 50, (5, 170, 0)),      # sem subir de nível
    (5, 450, 50, (6, 0, 1)),        # exatamente no limite (5*100)
    (5, 480, 50, (6, 30, 1)),       # sobra de XP é preservada
    (1, 0, 350, (3, 50, 2)),        # sobe múltiplos níveis de uma vez
    (99, 0, 100000, (100, 0, 1)),   # trava no nível máximo
    (100, 0, 50, (100, 0, 0)),      # já no máximo
])
def test_calcular_progressao(nivel, exp, ganho, esperado):
    assert calcular_progressao(nivel, exp, ganho) == esperado

def test_xp_necessario_cresce_com_nivel():
    assert xp_para_proximo_nivel(1) < xp_para_proximo_nivel(2) < xp_para_proximo_nivel(50)

@pytest.mark.parametrize("args", [(5, 0, -1), (0, 0, 10), (101, 0, 10)])
def test_entradas_invalidas(args):
    with pytest.raises(ValueError):
        calcular_progressao(*args)

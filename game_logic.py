"""Regras de progressão (funções puras, sem banco)."""
MAX_NIVEL = 100

def xp_para_proximo_nivel(nivel: int) -> int:
    return nivel * 100

def calcular_progressao(nivel: int, experiencia: int, ganho: int):
    """Retorna (novo_nivel, nova_experiencia, niveis_ganhos)."""
    if ganho < 0:
        raise ValueError("ganho de XP não pode ser negativo")
    if not 1 <= nivel <= MAX_NIVEL:
        raise ValueError("nível fora do intervalo 1..100")
    n, exp = nivel, experiencia + ganho
    while n < MAX_NIVEL and exp >= xp_para_proximo_nivel(n):
        exp -= xp_para_proximo_nivel(n)
        n += 1
    if n == MAX_NIVEL:
        exp = 0
    return n, exp, n - nivel

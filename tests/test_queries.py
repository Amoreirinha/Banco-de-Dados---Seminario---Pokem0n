"""As 4 consultas do seed.sql devolvem o esperado nos dados de teste."""
import pytest
pytestmark = pytest.mark.db

def test_q1_perfil(q):
    r = q("""SELECT j.nome_usuario, p.apelido, p.nivel, e.nome AS especie
             FROM jogador j JOIN personagem p ON p.id_jogador = j.id_jogador
             JOIN especie e ON e.id_especie = p.id_especie WHERE j.id_jogador = 1""")
    assert r == [{"nome_usuario": "ash_ketchum", "apelido": "Chama", "nivel": 5, "especie": "Charmander"}]

def test_q2_auditoria_mais_recente_primeiro(q):
    r = q("""SELECT tipo_evento FROM progressao WHERE id_personagem = 1
             ORDER BY "timestamp" DESC, id_progresso DESC""")
    assert [x["tipo_evento"] for x in r] == ["SUBIU_NIVEL", "CAPTURA_POKEMON"]

def test_q3_inventario(q):
    r = q("""SELECT i.nome, i.raridade, inv.quantidade FROM inventario inv
             JOIN item i ON i.id_item = inv.id_item WHERE inv.id_jogador = 1 ORDER BY inv.slot""")
    assert [(x["nome"], x["quantidade"]) for x in r] == [("Poção", 5), ("Pokébola", 10)]

def test_q4_ranking(q):
    r = q("""SELECT j.nome_usuario, COALESCE(SUM(p.nivel),0) AS total_niveis FROM jogador j
             LEFT JOIN personagem p ON p.id_jogador = j.id_jogador
             GROUP BY j.id_jogador ORDER BY total_niveis DESC""")
    assert [(x["nome_usuario"], x["total_niveis"]) for x in r] == [("misty_water", 18), ("ash_ketchum", 5)]

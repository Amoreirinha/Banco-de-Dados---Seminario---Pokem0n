"""Testes do esquema: integridade, constraints e atomicidade (ACID)."""
import os
import pytest, psycopg2
from psycopg2 import errors

pytestmark = pytest.mark.db

def test_seed_quantidades(q):
    cont = lambda t: q(f"SELECT count(*) AS n FROM {t}")[0]["n"]
    assert cont("jogador") == 2 and cont("especie") == 3 and cont("personagem") == 2
    assert cont("ginasio") == 1 and cont("conquista") == 1 and cont("progressao") >= 2

def test_autorrelacionamento_evolucao(q):
    r = q("SELECT e.nome, ev.nome AS prox FROM especie e JOIN especie ev ON ev.id_especie = e.evolui_para ORDER BY e.id_especie")
    assert [(x["nome"], x["prox"]) for x in r] == [("Charmander", "Charmeleon"), ("Charmeleon", "Charizard")]

def test_personagem_exige_jogador_existente(q):
    with pytest.raises(errors.ForeignKeyViolation):
        q("INSERT INTO personagem (apelido, hp_atual, id_especie, id_jogador) VALUES ('X', 10, 1, 999)")

def test_inventario_pk_composta(q):
    with pytest.raises(errors.UniqueViolation):
        q("INSERT INTO inventario (id_jogador, id_item, quantidade) VALUES (1, 1, 1)")

def test_inventario_quantidade_nao_negativa(q):
    with pytest.raises(errors.CheckViolation):
        q("UPDATE inventario SET quantidade = -1 WHERE id_jogador = 1 AND id_item = 1")

def test_nivel_dentro_do_limite(q):
    with pytest.raises(errors.CheckViolation):
        q("UPDATE personagem SET nivel = 101 WHERE id_personagem = 1")

def test_conquista_unica_por_ginasio(q):
    with pytest.raises(errors.UniqueViolation):
        q("INSERT INTO conquista (id_jogador, id_ginasio) VALUES (1, 1)")

def test_usuario_e_email_unicos(q):
    with pytest.raises(errors.UniqueViolation):
        q("INSERT INTO jogador (nome_usuario, email) VALUES ('ash_ketchum', 'novo@x.com')")
    with pytest.raises(errors.UniqueViolation):
        q("INSERT INTO jogador (nome_usuario, email) VALUES ('novo', 'ash@pallet.com')")

def test_auditoria_nao_some_com_o_jogador(q):
    """Jogador com histórico de progressão não pode ser apagado (log preservado)."""
    with pytest.raises(errors.ForeignKeyViolation):
        q("DELETE FROM jogador WHERE id_jogador = 1")

def test_transacao_atomica_rollback(db, q):
    """UPDATE seguido de INSERT inválido: nada pode ser persistido (o 'A' do ACID)."""
    antes = q("SELECT experiencia FROM personagem WHERE id_personagem = 1")[0]["experiencia"]
    c = psycopg2.connect(os.environ["TEST_DATABASE_URL"])  # conexão própria, SEM autocommit (db.dsn mascara a senha)
    try:
        cur = c.cursor()
        cur.execute("UPDATE personagem SET experiencia = experiencia + 50 WHERE id_personagem = 1")
        with pytest.raises(errors.ForeignKeyViolation):
            cur.execute("""INSERT INTO progressao (tipo_evento, entidade_ref, id_personagem, id_jogador)
                           VALUES ('GANHO_XP', 'experiencia', 1, 999)""")
        c.rollback()
    finally:
        c.close()
    assert q("SELECT experiencia FROM personagem WHERE id_personagem = 1")[0]["experiencia"] == antes

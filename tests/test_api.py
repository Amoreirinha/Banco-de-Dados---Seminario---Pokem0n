"""Testes das rotas Flask (integração com o banco de teste)."""
import pytest
pytestmark = pytest.mark.db

def test_index_serve_dashboard(client):
    r = client.get("/")
    assert r.status_code == 200 and "PokéDB" in r.get_data(as_text=True)

def test_lista_jogadores(client):
    assert [j["nome_usuario"] for j in client.get("/api/jogadores").get_json()] == ["ash_ketchum", "misty_water"]

def test_perfil(client):
    p = client.get("/api/jogador/1/perfil").get_json()[0]
    assert p["apelido"] == "Chama" and p["especie"] == "Charmander"
    assert p["evolui_para"] == "Charmeleon" and p["nivel_evolucao"] == 16
    assert p["tipo_primario"] == "Fogo" and p["status_base"]["hp"] == 39

def test_perfil_jogador_inexistente(client):
    assert client.get("/api/jogador/999/perfil").get_json() == []

def test_historico_ordenado(client):
    h = client.get("/api/personagem/1/historico").get_json()
    assert [x["tipo_evento"] for x in h] == ["SUBIU_NIVEL", "CAPTURA_POKEMON"]

def test_inventario(client):
    inv = client.get("/api/jogador/2/inventario").get_json()
    assert [(i["nome"], i["raridade"], i["quantidade"]) for i in inv] == [("Poção", "Comum", 2), ("Pedra de Fogo", "Rara", 1)]

def test_ranking(client):
    assert [r["nome_usuario"] for r in client.get("/api/ranking").get_json()] == ["misty_water", "ash_ketchum"]

def test_ganhar_xp_sem_subir_nivel(client, q):
    r = client.post("/api/personagem/1/ganhar-xp").get_json()
    assert r["ok"] and r["subiu_nivel"] is False and r["experiencia"] == 170
    h = client.get("/api/personagem/1/historico").get_json()
    assert len(h) == 3 and h[0]["tipo_evento"] == "GANHO_XP"
    assert (h[0]["valor_anterior"], h[0]["valor_novo"]) == ("120", "170")

def test_ganhar_xp_subindo_de_nivel(client, q):
    q("UPDATE personagem SET experiencia = 480 WHERE id_personagem = 1")
    r = client.post("/api/personagem/1/ganhar-xp").get_json()
    assert r["subiu_nivel"] and (r["nivel"], r["experiencia"]) == (6, 30)
    h = client.get("/api/personagem/1/historico").get_json()
    assert [x["tipo_evento"] for x in h[:2]] == ["SUBIU_NIVEL", "GANHO_XP"]
    assert (h[0]["valor_anterior"], h[0]["valor_novo"]) == ("5", "6")

def test_ganhar_xp_personagem_inexistente(client):
    assert client.post("/api/personagem/999/ganhar-xp").status_code == 404

def test_ganhar_xp_exige_post(client):
    assert client.get("/api/personagem/1/ganhar-xp").status_code == 405

def test_falha_na_auditoria_desfaz_o_update(client, q):
    """Se o INSERT em PROGRESSAO falhar, o UPDATE do personagem também é desfeito."""
    q("""CREATE OR REPLACE FUNCTION falha() RETURNS trigger AS $$ BEGIN RAISE EXCEPTION 'falha simulada'; END $$ LANGUAGE plpgsql;
         CREATE TRIGGER t_falha BEFORE INSERT ON progressao FOR EACH ROW
         WHEN (NEW.tipo_evento = 'GANHO_XP') EXECUTE FUNCTION falha();""")
    try:
        r = client.post("/api/personagem/1/ganhar-xp")
    finally:
        q("DROP FUNCTION IF EXISTS falha() CASCADE")   # não deixa lixo no banco de teste
    assert r.status_code == 500 and "erro" in r.get_json()
    p = q("SELECT nivel, experiencia FROM personagem WHERE id_personagem = 1")[0]
    assert (p["nivel"], p["experiencia"]) == (5, 120)
    assert q("SELECT count(*) AS n FROM progressao WHERE id_personagem = 1")[0]["n"] == 2

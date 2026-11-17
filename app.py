"""Backend Flask - Protótipo Grupo 11 / Equipe 13"""
import os
import psycopg2, psycopg2.extras
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")
from game_logic import calcular_progressao

def dsn():
    return os.getenv("DATABASE_URL", "dbname=pokemon_db user=postgres password=postgres host=localhost")

def conn():
    return psycopg2.connect(dsn(), cursor_factory=psycopg2.extras.RealDictCursor)

def query(sql, params=()):
    with conn() as c, c.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/jogadores")
def jogadores():
    return jsonify(query("SELECT id_jogador, nome_usuario FROM jogador ORDER BY 1"))

# Query 1 - Perfil
@app.route("/api/jogador/<int:jid>/perfil")
def perfil(jid):
    return jsonify(query("""
        SELECT j.nome_usuario, p.id_personagem, p.apelido, p.nivel, p.experiencia, p.hp_atual,
               e.nome AS especie, e.tipo_primario, e.tipo_secundario, e.status_base,
               e.nivel_evolucao, ev.nome AS evolui_para
        FROM jogador j JOIN personagem p ON p.id_jogador = j.id_jogador
        JOIN especie e ON e.id_especie = p.id_especie
        LEFT JOIN especie ev ON ev.id_especie = e.evolui_para
        WHERE j.id_jogador = %s ORDER BY p.slot_equipe""", (jid,)))

# Query 2 - Auditoria
@app.route("/api/personagem/<int:pid>/historico")
def historico(pid):
    rows = query("""SELECT tipo_evento, entidade_ref, valor_anterior, valor_novo, "timestamp"
                    FROM progressao WHERE id_personagem = %s ORDER BY "timestamp" DESC, id_progresso DESC""", (pid,))
    for r in rows: r["timestamp"] = r["timestamp"].strftime("%d/%m/%Y %H:%M:%S")
    return jsonify(rows)

# Query 3 - Inventário
@app.route("/api/jogador/<int:jid>/inventario")
def inventario(jid):
    return jsonify(query("""SELECT i.nome, i.raridade, inv.quantidade
                            FROM inventario inv JOIN item i ON i.id_item = inv.id_item
                            WHERE inv.id_jogador = %s ORDER BY inv.slot""", (jid,)))

# Query 4 - Ranking
@app.route("/api/ranking")
def ranking():
    return jsonify(query("""SELECT j.nome_usuario, COALESCE(SUM(p.nivel),0)::int AS total_niveis
                            FROM jogador j LEFT JOIN personagem p ON p.id_jogador = j.id_jogador
                            GROUP BY j.id_jogador ORDER BY total_niveis DESC"""))

# Ação: UPDATE + INSERT na auditoria, em UMA transação (ACID)
@app.route("/api/personagem/<int:pid>/ganhar-xp", methods=["POST"])
def ganhar_xp(pid):
    XP = 50
    c = conn()
    try:
        with c, c.cursor() as cur:   # commit se OK, rollback se exceção
            cur.execute("SELECT nivel, experiencia, id_jogador FROM personagem WHERE id_personagem=%s FOR UPDATE", (pid,))
            p = cur.fetchone()
            if not p:
                return jsonify(erro="Personagem não encontrado"), 404
            nivel, exp, ganhos = calcular_progressao(p["nivel"], p["experiencia"], XP)
            cur.execute("UPDATE personagem SET nivel=%s, experiencia=%s WHERE id_personagem=%s", (nivel, exp, pid))
            ins = """INSERT INTO progressao (tipo_evento, entidade_ref, valor_anterior, valor_novo, "timestamp", id_personagem, id_jogador)
                     VALUES (%s,%s,%s,%s,clock_timestamp(),%s,%s)"""
            cur.execute(ins, ("GANHO_XP", "experiencia", p["experiencia"], p["experiencia"] + XP, pid, p["id_jogador"]))
            if ganhos:
                cur.execute(ins, ("SUBIU_NIVEL", "nivel", p["nivel"], nivel, pid, p["id_jogador"]))
        return jsonify(ok=True, nivel=nivel, experiencia=exp, xp_ganho=XP, subiu_nivel=ganhos > 0)
    finally:
        c.close()

@app.errorhandler(psycopg2.Error)
def erro_banco(e):
    return jsonify(erro="Erro no banco de dados", detalhe=str(e).splitlines()[0]), 500

if __name__ == "__main__":
    app.run(debug=True)

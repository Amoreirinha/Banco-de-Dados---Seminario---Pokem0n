-- =====================================================================
-- PARTE 2: DML - dados de teste + 4 consultas
-- Uso: psql -d pokemon_db -f seed.sql
-- =====================================================================
INSERT INTO jogador (nome_usuario, email, ultimo_login, regiao_inicial) VALUES
 ('ash_ketchum', 'ash@pallet.com', now(), 'Kanto'),
 ('misty_water', 'misty@cerulean.com', now(), 'Kanto');

-- Cadeia evolutiva: Charmander(1) -> Charmeleon(2) -> Charizard(3). Inserir do fim p/ o início.
INSERT INTO especie (id_especie, nome, tipo_primario, tipo_secundario, status_base, evolui_para, nivel_evolucao) VALUES
 (3, 'Charizard',  'Fogo', 'Voador', '{"hp":78,"atk":84,"def":78}', NULL, NULL),
 (2, 'Charmeleon', 'Fogo', NULL,     '{"hp":58,"atk":64,"def":58}', 3, 36),
 (1, 'Charmander', 'Fogo', NULL,     '{"hp":39,"atk":52,"def":43}', 2, 16);
SELECT setval('especie_id_especie_seq', 3);

INSERT INTO personagem (apelido, nivel, experiencia, hp_atual, status, slot_equipe, id_especie, id_jogador) VALUES
 ('Chama', 5,  120, 39, 'normal', 1, 1, 1),
 ('Brasa', 18, 450, 58, 'normal', 1, 2, 2);

INSERT INTO item (nome, categoria, raridade) VALUES
 ('Poção', 'Cura', 'Comum'), ('Pokébola', 'Captura', 'Comum'), ('Pedra de Fogo', 'Evolução', 'Rara');
INSERT INTO inventario (id_jogador, id_item, quantidade, slot) VALUES
 (1,1,5,1),(1,2,10,2),(2,1,2,1),(2,3,1,2);

INSERT INTO ginasio (nome, lider, regiao) VALUES ('Ginásio de Pewter', 'Brock', 'Kanto');
INSERT INTO conquista (id_jogador, id_ginasio) VALUES (1, 1);
INSERT INTO sessao (inicio, fim, dispositivo, ip_origem, id_jogador) VALUES
 (now() - interval '2 hours', now() - interval '1 hour', 'Android', '177.10.20.30', 1);

INSERT INTO progressao (tipo_evento, entidade_ref, valor_anterior, valor_novo, "timestamp", id_personagem, id_jogador) VALUES
 ('CAPTURA_POKEMON', 'especie:Charmander', NULL, 'capturado', now() - interval '3 hours', 1, 1),
 ('SUBIU_NIVEL',     'nivel',               '4',  '5',        now() - interval '1 hour',  1, 1);

-- ---------------- CONSULTAS (usadas pela aplicação web) ----------------
-- Q1 Perfil
SELECT j.nome_usuario, p.apelido, p.nivel, e.nome AS especie
FROM jogador j JOIN personagem p ON p.id_jogador = j.id_jogador
JOIN especie e ON e.id_especie = p.id_especie WHERE j.id_jogador = 1;

-- Q2 Auditoria (mais recente primeiro)
SELECT tipo_evento, entidade_ref, valor_anterior, valor_novo, "timestamp"
FROM progressao WHERE id_personagem = 1 ORDER BY "timestamp" DESC, id_progresso DESC;

-- Q3 Inventário
SELECT i.nome, i.raridade, inv.quantidade
FROM inventario inv JOIN item i ON i.id_item = inv.id_item
WHERE inv.id_jogador = 1 ORDER BY inv.slot;

-- Q4 Ranking
SELECT j.nome_usuario, COALESCE(SUM(p.nivel),0) AS total_niveis
FROM jogador j LEFT JOIN personagem p ON p.id_jogador = j.id_jogador
GROUP BY j.id_jogador ORDER BY total_niveis DESC;

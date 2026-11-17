-- =====================================================================
-- PARTE 1: DDL (PostgreSQL) - Grupo 11 / Equipe 13
-- Uso: createdb pokemon_db && psql -d pokemon_db -f schema.sql
-- =====================================================================
DROP TABLE IF EXISTS conquista, inventario, progressao, sessao, personagem, ginasio, item, especie, jogador CASCADE;

CREATE TABLE jogador (
  id_jogador     SERIAL PRIMARY KEY,
  nome_usuario   VARCHAR(30)  NOT NULL UNIQUE,
  email          VARCHAR(120) NOT NULL UNIQUE,
  data_cadastro  TIMESTAMP    NOT NULL DEFAULT now(),
  ultimo_login   TIMESTAMP,
  regiao_inicial VARCHAR(30)
);

CREATE TABLE especie (
  id_especie      SERIAL PRIMARY KEY,
  nome            VARCHAR(40) NOT NULL UNIQUE,
  tipo_primario   VARCHAR(20) NOT NULL,
  tipo_secundario VARCHAR(20),
  status_base     JSONB,                                   -- hp, ataque, defesa...
  evolui_para     INT REFERENCES especie(id_especie),      -- auto-relacionamento
  nivel_evolucao  INT CHECK (nivel_evolucao > 0)
);

CREATE TABLE personagem (
  id_personagem SERIAL PRIMARY KEY,
  apelido       VARCHAR(30) NOT NULL,
  nivel         INT NOT NULL DEFAULT 1 CHECK (nivel BETWEEN 1 AND 100),
  experiencia   INT NOT NULL DEFAULT 0 CHECK (experiencia >= 0),
  hp_atual      INT NOT NULL CHECK (hp_atual >= 0),
  status        VARCHAR(20) NOT NULL DEFAULT 'normal',
  slot_equipe   INT CHECK (slot_equipe BETWEEN 1 AND 6),
  id_especie    INT NOT NULL REFERENCES especie(id_especie),
  id_jogador    INT NOT NULL REFERENCES jogador(id_jogador) ON DELETE CASCADE
);

-- Entidade central de AUDITORIA (log imutável de eventos)
CREATE TABLE progressao (
  id_progresso   BIGSERIAL PRIMARY KEY,
  tipo_evento    VARCHAR(40) NOT NULL,
  entidade_ref   VARCHAR(40) NOT NULL,
  valor_anterior VARCHAR(60),
  valor_novo     VARCHAR(60),
  "timestamp"    TIMESTAMP NOT NULL DEFAULT now(),
  id_personagem  INT REFERENCES personagem(id_personagem),
  id_jogador     INT NOT NULL REFERENCES jogador(id_jogador)
);
CREATE INDEX idx_prog_personagem_data ON progressao(id_personagem, "timestamp" DESC);

CREATE TABLE item (
  id_item   SERIAL PRIMARY KEY,
  nome      VARCHAR(40) NOT NULL UNIQUE,
  categoria VARCHAR(30) NOT NULL,
  raridade  VARCHAR(20) NOT NULL
);

CREATE TABLE inventario (
  id_jogador INT NOT NULL REFERENCES jogador(id_jogador) ON DELETE CASCADE,
  id_item    INT NOT NULL REFERENCES item(id_item),
  quantidade INT NOT NULL CHECK (quantidade >= 0),         -- nunca negativo
  slot       INT,
  PRIMARY KEY (id_jogador, id_item)                        -- PK composta
);

CREATE TABLE ginasio (
  id_ginasio SERIAL PRIMARY KEY,
  nome       VARCHAR(40) NOT NULL,
  lider      VARCHAR(40) NOT NULL,
  regiao     VARCHAR(30) NOT NULL
);

CREATE TABLE conquista (
  id_conquista   SERIAL PRIMARY KEY,
  data_conquista TIMESTAMP NOT NULL DEFAULT now(),
  id_jogador     INT NOT NULL REFERENCES jogador(id_jogador),
  id_ginasio     INT NOT NULL REFERENCES ginasio(id_ginasio),
  UNIQUE (id_jogador, id_ginasio)                          -- 1 insígnia por ginásio
);

CREATE TABLE sessao (
  id_sessao   SERIAL PRIMARY KEY,
  inicio      TIMESTAMP NOT NULL DEFAULT now(),
  fim         TIMESTAMP,
  dispositivo VARCHAR(30),
  ip_origem   VARCHAR(45),
  id_jogador  INT NOT NULL REFERENCES jogador(id_jogador)
);

# PokéDB - Grupo 11 / Equipe 13
## Instalação
1. Instale PostgreSQL 14+ e Python 3.10+.
2. `createdb -U postgres pokemon_db`
3. `psql -U postgres -d pokemon_db -f schema.sql`
4. `psql -U postgres -d pokemon_db -f seed.sql`
5. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
6. `pip install -r requirements.txt`
7. Ajuste a conexão se necessário: `export DATABASE_URL="dbname=pokemon_db user=postgres password=SUASENHA host=localhost"`
8. `python app.py` e abra http://127.0.0.1:5000

## Testes automáticos
```bash
pip install -r requirements-dev.txt
createdb -U postgres pokemon_test            # banco SEPARADO (o nome precisa conter "test")
export TEST_DATABASE_URL="dbname=pokemon_test user=postgres password=postgres host=localhost"
pytest -v
```
- `test_game_logic.py`: regras de XP/nível (sem banco; roda sempre).
- `test_database.py`: FKs, PK composta, CHECK, UNIQUE, auditoria preservada, rollback (ACID).
- `test_queries.py`: as 4 consultas do seed.
- `test_api.py`: rotas Flask, ação "Ganhar XP", erro 404/405 e rollback quando a auditoria falha.
Sem `TEST_DATABASE_URL`, os testes de banco são ignorados (skip). O banco de teste é recriado a cada teste.

### Windows (PowerShell)
```powershell
$env:TEST_DATABASE_URL = "dbname=pokemon_test user=postgres password=SUA_SENHA host=localhost"
$env:DATABASE_URL      = "dbname=pokemon_db user=postgres password=SUA_SENHA host=localhost"
```
A senha é a que você definiu ao instalar o PostgreSQL (não necessariamente `postgres`).
Se aparecer `UnicodeDecodeError ... 0xe7`, é a mensagem de erro do servidor em português (ex.: "autenticação falhou"):
confira a senha e se o banco existe (`psql -U postgres -h localhost -l`).

## Relatório final dos testes
Toda execução do `pytest` gera automaticamente o arquivo **`relatorio_testes.txt`** (na raiz do projeto), com:
ambiente (Python, pytest, versão do PostgreSQL), resumo (passou/falhou/ignorado), cada teste com
**o que verifica e por que importa**, o motivo de cada falha, e uma seção final dizendo quais pilares da
justificativa técnica (integridade referencial, ACID, auditoria...) foram comprovados.
- Para mudar o destino: `$env:RELATORIO_PATH = "C:\caminho\relatorio.txt"` (PowerShell) ou `export RELATORIO_PATH=...`.
- O relatório nunca inclui a senha do banco.
- Código do relatório: `tests/relatorio.py` (coleta), `tests/relatorio_core.py` (texto) e `tests/explicacoes.py` (explicações; edite para ajustar o texto).

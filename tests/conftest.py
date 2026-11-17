import os, pathlib, sys
import pytest, psycopg2, psycopg2.extras

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
# plugin que gera o relatório final (relatorio_testes.txt) ao fim de cada execução
from relatorio import pytest_sessionstart, pytest_runtest_makereport, pytest_terminal_summary  # noqa: E402,F401

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST_DSN = os.getenv("TEST_DATABASE_URL")

@pytest.fixture
def db():
    """Conexão (autocommit) com um banco de TESTE recriado do zero (schema + seed) a cada teste."""
    if not TEST_DSN:
        pytest.skip("defina TEST_DATABASE_URL para rodar os testes de banco")
    if "test" not in TEST_DSN.lower():
        pytest.fail("TEST_DATABASE_URL deve apontar para um banco com 'test' no nome (evita apagar dados reais)")
    try:
        conn = psycopg2.connect(TEST_DSN, cursor_factory=psycopg2.extras.RealDictCursor)
    except psycopg2.OperationalError as e:
        pytest.skip(f"PostgreSQL de teste indisponível: {e}")
    except UnicodeDecodeError:
        # Windows com PostgreSQL em português: a mensagem de erro do servidor vem em cp1252 e o
        # psycopg2 não consegue decodificá-la. O erro REAL costuma ser senha errada (ou banco inexistente).
        pytest.fail("Falha ao conectar no PostgreSQL de teste (mensagem de erro ilegível por causa do idioma do Windows). "
                    "Verifique a senha em TEST_DATABASE_URL e se o banco existe: psql -U postgres -h localhost -d pokemon_test")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP FUNCTION IF EXISTS falha() CASCADE")   # resto de execuções anteriores
        cur.execute((ROOT / "schema.sql").read_text(encoding="utf-8"))
        cur.execute((ROOT / "seed.sql").read_text(encoding="utf-8"))
    yield conn
    conn.close()

@pytest.fixture
def q(db):
    """q(sql, params) -> lista de dicts."""
    def run(sql, params=()):
        with db.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if cur.description else []
    return run

@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DSN)
    import app as app_module
    app_module.app.config.update(TESTING=False)  # exceções viram resposta 500 (errorhandler)
    return app_module.app.test_client()

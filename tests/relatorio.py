"""Plugin do pytest: coleta os resultados e grava o relatório final em texto ao término da execução."""
import os, time, platform, pathlib, datetime
import pytest
from relatorio_core import gerar_relatorio
from explicacoes import EXPLICACOES, GRUPOS, PILARES

ROOT = pathlib.Path(__file__).resolve().parent.parent
_resultados = []
_inicio = [time.time()]

def pytest_sessionstart(session):
    _resultados.clear()
    _inicio[0] = time.time()

def _registrar(item, rep, status):
    detalhe = ""
    if status in ("FALHOU", "ERRO"):
        crash = getattr(rep.longrepr, "reprcrash", None)
        detalhe = crash.message if crash else str(rep.longrepr)
        detalhe = " ".join(detalhe.split())[:500]
    elif status == "IGNORADO":
        lr = rep.longrepr
        detalhe = str(lr[2] if isinstance(lr, tuple) and len(lr) >= 3 else lr).replace("Skipped: ", "")
    callspec = getattr(item, "callspec", None)
    _resultados.append({
        "arquivo": item.path.stem,
        "nome": getattr(item, "originalname", None) or item.name,
        "param": callspec.id if callspec else "",
        "status": status,
        "duracao": rep.duration,
        "detalhe": detalhe,
        "doc": (item.function.__doc__ or "").strip() if hasattr(item, "function") else "",
    })

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        _registrar(item, rep, {"passed": "PASSOU", "failed": "FALHOU", "skipped": "IGNORADO"}[rep.outcome])
    elif rep.when == "setup" and rep.skipped:
        _registrar(item, rep, "IGNORADO")
    elif rep.when == "setup" and rep.failed:
        _registrar(item, rep, "ERRO")
    elif rep.when == "teardown" and rep.failed:
        _registrar(item, rep, "ERRO")

def _versao_banco():
    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        return "não configurado (TEST_DATABASE_URL ausente)", "-"
    try:
        import psycopg2, psycopg2.extensions
        info = psycopg2.extensions.parse_dsn(dsn)
        alvo = f"{info.get('dbname', '?')} @ {info.get('host', 'local')}"   # nunca inclui a senha
        with psycopg2.connect(dsn, connect_timeout=3) as c, c.cursor() as cur:
            cur.execute("SHOW server_version")
            return f"PostgreSQL {cur.fetchone()[0]}", alvo
    except Exception:
        return "indisponível (não foi possível conectar)", "-"

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not _resultados:
        return
    versao, alvo = _versao_banco()
    meta = {
        "Data/hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Sistema operacional": f"{platform.system()} {platform.release()}",
        "Python": platform.python_version(),
        "pytest": pytest.__version__,
        "Banco de dados": versao,
        "Banco de teste": alvo,
        "_duracao": f"{time.time() - _inicio[0]:.2f}s",
    }
    texto = gerar_relatorio(_resultados, meta, EXPLICACOES, GRUPOS, PILARES)
    destino = pathlib.Path(os.getenv("RELATORIO_PATH", ROOT / "relatorio_testes.txt"))
    destino.write_text(texto, encoding="utf-8-sig")   # BOM: abre com acentos corretos no Bloco de Notas
    terminalreporter.write_sep("=", "relatório final gerado")
    terminalreporter.write_line(f"Relatório salvo em: {destino}")

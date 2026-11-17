"""Gera o texto do relatório final (sem depender do pytest, para ser fácil de testar)."""
import textwrap
from collections import OrderedDict

LARG = 100
ICONE = {"PASSOU": "[ OK ]", "FALHOU": "[FALHA]", "ERRO": "[ERRO ]", "IGNORADO": "[PULOU]"}

def _p(texto, ind="", sub=None):
    return textwrap.fill(texto, LARG, initial_indent=ind, subsequent_indent=sub if sub is not None else ind)

def _veredito_pilar(nomes, resultados):
    rel = [r for r in resultados if r["nome"] in nomes]
    if not rel:
        return "NÃO EXECUTADO"
    if any(r["status"] in ("FALHOU", "ERRO") for r in rel):
        return "NÃO COMPROVADO (há testes falhando)"
    if any(r["status"] == "IGNORADO" for r in rel):
        return "PARCIAL (testes ignorados)"
    achados = {r["nome"] for r in rel}
    if len(achados) < len(set(nomes)):
        return f"PARCIAL ({len(achados)} de {len(set(nomes))} testes executados)"
    return "COMPROVADO"

def gerar_relatorio(resultados, meta, explicacoes, grupos, pilares):
    cont = lambda s: sum(1 for r in resultados if r["status"] == s)
    total, ok, falhas, erros, pulou = len(resultados), cont("PASSOU"), cont("FALHOU"), cont("ERRO"), cont("IGNORADO")
    aprovado = total > 0 and falhas == 0 and erros == 0 and ok > 0
    L = []
    add = L.append
    linha = "=" * LARG
    add(linha)
    add("RELATÓRIO FINAL DE TESTES AUTOMÁTICOS")
    add("Projeto: Bancos de Dados na Indústria de Jogos (PokéDB) - Grupo 11 / Equipe 13")
    add(linha)
    add("")
    add("1. AMBIENTE")
    add("-" * LARG)
    for k, v in meta.items():
        if k.startswith("_"):
            continue
        add(f"  {k:<22}: {v}")
    add("")
    add("2. RESUMO")
    add("-" * LARG)
    add(f"  Total de testes ....: {total}")
    add(f"  Passaram ...........: {ok}")
    add(f"  Falharam ...........: {falhas}")
    add(f"  Erros de preparação : {erros}")
    add(f"  Ignorados ..........: {pulou}")
    add(f"  Tempo total ........: {meta.get('_duracao', '?')}")
    add(f"  RESULTADO GERAL ....: {'APROVADO' if aprovado else 'REPROVADO / INCOMPLETO'}")
    if pulou:
        add(_p("  Atenção: testes ignorados normalmente significam que TEST_DATABASE_URL não foi definida; "
               "os testes de banco só rodam com um PostgreSQL de teste.", "  ", "  "))
    add("")
    add("3. RESULTADO DETALHADO (o que cada teste verifica e por que importa)")
    add("-" * LARG)
    por_grupo = OrderedDict((g, []) for g in grupos)
    for r in resultados:
        por_grupo.setdefault(r["arquivo"], []).append(r)
    n = 0
    for g, itens in por_grupo.items():
        if not itens:
            continue
        add("")
        add(f"## {grupos.get(g, g)}")
        for r in itens:
            n += 1
            rotulo = r["nome"] + (f"  [{r['param']}]" if r["param"] else "")
            add("")
            add(f"{n:>2}. {ICONE[r['status']]} {rotulo}  ({r['duracao']:.2f}s)")
            verifica, importa = explicacoes.get(r["nome"], (r["doc"] or "(sem descrição)", ""))
            add(_p("O que verifica: " + verifica, "      ", " " * 22))
            if importa:
                add(_p("Por que importa: " + importa, "      ", " " * 23))
            if r["status"] in ("FALHOU", "ERRO"):
                add(_p("DETALHE DO PROBLEMA: " + (r["detalhe"] or "(sem detalhe)"), "      ", "      "))
            elif r["status"] == "IGNORADO":
                add(_p("Motivo: " + (r["detalhe"] or "ignorado"), "      ", "      "))
    add("")
    add("4. O QUE ESTES TESTES COMPROVAM (justificativa técnica para o banco relacional)")
    add("-" * LARG)
    for titulo, nomes in pilares:
        add(f"  - {titulo}: {_veredito_pilar(nomes, resultados)}")
    add("")
    add("5. CONCLUSÃO")
    add("-" * LARG)
    if aprovado and not pulou:
        add(_p("Todos os testes passaram. O banco relacional (PostgreSQL) garantiu integridade referencial, regras "
               "protegidas por constraints, transações atômicas (ACID) e uma trilha de auditoria confiável. Em especial, "
               "os testes de rollback mostram que, se qualquer parte de uma operação falhar, nada é gravado pela metade: "
               "não há XP ou item perdido/duplicado sem registro. Essa consistência forte é o motivo pelo qual a indústria "
               "de jogos usa bancos relacionais para dados críticos como inventário, economia e progressão.", "  "))
    elif aprovado:
        add(_p("Os testes executados passaram, mas houve testes ignorados; rode novamente com o banco de teste "
               "configurado para obter a validação completa.", "  "))
    else:
        add(_p("Há testes falhando. Veja os itens marcados com [FALHA] ou [ERRO ] na seção 3, corrija e execute "
               "novamente; este relatório é regenerado a cada execução do pytest.", "  "))
    add("")
    add(linha)
    return "\n".join(L) + "\n"

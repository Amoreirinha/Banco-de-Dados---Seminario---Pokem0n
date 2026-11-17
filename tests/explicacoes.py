"""Textos que aparecem no relatório final: para cada teste, o que ele verifica e por que importa."""

GRUPOS = {
    "test_game_logic": "REGRAS DE JOGO (lógica pura, sem banco)",
    "test_database": "BANCO DE DADOS: integridade, regras e atomicidade (ACID)",
    "test_queries": "CONSULTAS SQL (as 4 queries do projeto)",
    "test_api": "APLICAÇÃO WEB (rotas Flask integradas ao banco)",
}

# nome do teste -> (o que verifica, por que importa para jogos)
EXPLICACOES = {
    # ---- lógica de jogo
    "test_calcular_progressao": (
        "A regra de XP/nível: sem subir, subir exatamente no limite, sobra de XP, subir vários níveis e travar no nível 100.",
        "A progressão é a base do jogo; um erro aqui geraria níveis errados para todos os jogadores."),
    "test_xp_necessario_cresce_com_nivel": (
        "Que o XP exigido aumenta a cada nível.",
        "Garante a curva de dificuldade (subir fica cada vez mais difícil)."),
    "test_entradas_invalidas": (
        "Que XP negativo ou nível fora de 1..100 é rejeitado com erro.",
        "Impede que bugs ou usuários mal-intencionados corrompam a progressão."),
    # ---- banco
    "test_seed_quantidades": (
        "Que os dados de teste foram carregados: 2 jogadores, 3 espécies, 2 personagens, 1 ginásio, 1 conquista e >= 2 progressões.",
        "Confirma que o script DDL + DML funciona do zero, em um banco vazio."),
    "test_autorrelacionamento_evolucao": (
        "Que ESPECIE se relaciona com ela mesma: Charmander -> Charmeleon -> Charizard.",
        "Mostra um relacionamento complexo (cadeia evolutiva) resolvido com FK e JOIN, sem duplicar dados."),
    "test_personagem_exige_jogador_existente": (
        "Que o banco recusa um personagem ligado a um jogador inexistente (violação de chave estrangeira).",
        "Integridade referencial: não existem personagens 'órfãos' nem dados inconsistentes."),
    "test_inventario_pk_composta": (
        "Que o mesmo item não pode ser inserido duas vezes no inventário do mesmo jogador (PK composta id_jogador + id_item).",
        "Evita duplicação de itens, que em jogos online vira fraude/exploit na economia."),
    "test_inventario_quantidade_nao_negativa": (
        "Que o banco recusa quantidade negativa de item (CHECK).",
        "A regra vale mesmo que a aplicação tenha um bug: o próprio banco protege a economia."),
    "test_nivel_dentro_do_limite": (
        "Que o banco recusa nível acima de 100 (CHECK).",
        "Impede 'cheaters' ou falhas de código de criarem personagens com nível impossível."),
    "test_conquista_unica_por_ginasio": (
        "Que um jogador não ganha duas vezes a insígnia do mesmo ginásio (UNIQUE).",
        "Evita conquistas duplicadas e rankings/estatísticas falsos."),
    "test_usuario_e_email_unicos": (
        "Que nome de usuário e e-mail não podem se repetir (UNIQUE).",
        "Garante identidade única por conta, essencial para login e suporte."),
    "test_auditoria_nao_some_com_o_jogador": (
        "Que um jogador com histórico de progressão não pode ser apagado.",
        "O log de auditoria é preservado: o suporte sempre consegue investigar o que aconteceu."),
    "test_transacao_atomica_rollback": (
        "Um UPDATE seguido de um INSERT inválido na mesma transação: nada pode ficar gravado após o erro.",
        "É o 'A' do ACID (Atomicidade): ou tudo acontece, ou nada. Impede itens/XP perdidos ou duplicados quando algo falha no meio."),
    # ---- queries
    "test_q1_perfil": (
        "Query 1: nome do jogador, personagem, nível e espécie (JOIN de 3 tabelas).",
        "Alimenta a tela de perfil do dashboard."),
    "test_q2_auditoria_mais_recente_primeiro": (
        "Query 2: histórico de progressão do personagem, do evento mais recente para o mais antigo.",
        "É a trilha de auditoria: 'o que o jogador fez e quando'."),
    "test_q3_inventario": (
        "Query 3: itens do jogador com nome, raridade e quantidade, na ordem dos slots.",
        "Alimenta a mochila do jogo."),
    "test_q4_ranking": (
        "Query 4: ranking por soma dos níveis (GROUP BY + SUM).",
        "Mostra agregação em SQL para rankings."),
    # ---- API
    "test_index_serve_dashboard": (
        "Que a página principal (dashboard) é entregue pelo servidor.",
        "Garante que o protótipo web abre."),
    "test_lista_jogadores": (
        "Que a rota de jogadores devolve os dois jogadores cadastrados.",
        "Alimenta o seletor de jogador da interface."),
    "test_perfil": (
        "Que a rota de perfil traz personagem, espécie, tipos, stats base e evolução vindos do banco.",
        "Prova que a interface exibe dados reais do banco, não valores fixos."),
    "test_perfil_jogador_inexistente": (
        "Que um jogador que não existe devolve lista vazia (sem erro).",
        "A aplicação trata entradas inesperadas com segurança."),
    "test_historico_ordenado": (
        "Que a rota de histórico devolve a auditoria ordenada do mais recente ao mais antigo.",
        "A tabela de auditoria da tela depende dessa ordem."),
    "test_inventario": (
        "Que a rota de inventário devolve os itens e quantidades corretos do jogador.",
        "Alimenta a mochila da interface."),
    "test_ranking": (
        "Que a rota de ranking devolve os jogadores ordenados pela soma dos níveis.",
        "Alimenta o ranking da interface."),
    "test_ganhar_xp_sem_subir_nivel": (
        "O botão 'Ganhar XP': atualiza a experiência e registra GANHO_XP na tabela de auditoria com valor anterior e novo.",
        "Demonstra UPDATE + INSERT de auditoria automáticos na mesma transação."),
    "test_ganhar_xp_subindo_de_nivel": (
        "Ao acumular XP suficiente, o nível sobe e são registrados GANHO_XP e SUBIU_NIVEL.",
        "Mostra a auditoria capturando cada mudança importante da progressão."),
    "test_ganhar_xp_personagem_inexistente": (
        "Que agir sobre um personagem que não existe devolve erro 404.",
        "Tratamento correto de erros na API."),
    "test_ganhar_xp_exige_post": (
        "Que a ação de ganhar XP só aceita POST (GET devolve 405).",
        "Ações que alteram dados não podem ser disparadas por um simples link."),
    "test_falha_na_auditoria_desfaz_o_update": (
        "Força uma falha ao gravar a auditoria e confere que o XP do personagem NÃO mudou (rollback) e a API devolve erro 500.",
        "Prova que progressão e auditoria andam juntas: nunca há XP ganho sem registro. É o argumento central pró-banco-relacional."),
}

# Pilares da justificativa técnica -> testes que os comprovam
PILARES = [
    ("Integridade referencial (FK, PK composta, UNIQUE)",
     ["test_personagem_exige_jogador_existente", "test_inventario_pk_composta", "test_conquista_unica_por_ginasio",
      "test_usuario_e_email_unicos", "test_autorrelacionamento_evolucao"]),
    ("Regras de negócio protegidas pelo próprio banco (CHECK)",
     ["test_inventario_quantidade_nao_negativa", "test_nivel_dentro_do_limite"]),
    ("Transações ACID (tudo ou nada)",
     ["test_transacao_atomica_rollback", "test_falha_na_auditoria_desfaz_o_update"]),
    ("Auditoria de progressão (anti-cheat e suporte)",
     ["test_auditoria_nao_some_com_o_jogador", "test_q2_auditoria_mais_recente_primeiro", "test_historico_ordenado",
      "test_ganhar_xp_sem_subir_nivel", "test_ganhar_xp_subindo_de_nivel"]),
    ("Consultas relacionais (JOIN, agregação)",
     ["test_q1_perfil", "test_q2_auditoria_mais_recente_primeiro", "test_q3_inventario", "test_q4_ranking"]),
    ("Aplicação web integrada ao banco",
     ["test_index_serve_dashboard", "test_lista_jogadores", "test_perfil", "test_inventario", "test_ranking",
      "test_ganhar_xp_exige_post", "test_ganhar_xp_personagem_inexistente"]),
    ("Regras de progressão do jogo",
     ["test_calcular_progressao", "test_xp_necessario_cresce_com_nivel", "test_entradas_invalidas"]),
]

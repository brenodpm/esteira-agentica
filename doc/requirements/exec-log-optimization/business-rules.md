# Regras de Negócio — Otimização via Exec Log

Status: approved
Owner: requirements
Last updated: 2026-06-19

## Inputs
- Issue #54: Base para otimização
- Histórico de comentários (2026-06-18)

## RN-001 — Escopo do Exec Log

**Descrição:** O arquivo `logs/exec.log` registra APENAS execuções de agentes de IA.

**Contexto:** Execução de agentes = chamadas de LLM que consomem tokens e requerem otimização. Movimentação de cards, sincronização de boards e ações mecânicas do sistema não são registradas.

**Exceções:** Nenhuma. Escopo é estritamente limitado a execuções de agentes IA.

## RN-002 — Formato de Linha do Exec Log

**Descrição:** Cada execução registra uma única linha com os campos separados por `;` (ponto-e-vírgula):
```
<issue_id>; <board_id>; <column_id>; <agent_id>; <model>; <effort>; <timestamp>; <duration_ms>; <tokens_used>
```

**Contexto:** Permite análise posterior pelo agente otimizador para identificar padrões de ineficiência.

**Exceções:** Nenhuma. Formato é rígido para compatibilidade com parser do otimizador.

## RN-003 — Critério de Ineficiência é Interpretativo

**Descrição:** O agente otimizador interpreta autonomamente o que constitui "tempo muito alto", "custo muito alto" ou "muitas repetições".

**Contexto:** Não existem thresholds numéricos pré-definidos. A decisão é contextual e depende do padrão observado no log histórico.

**Exceções:** Nenhuma. Escopo é delegado à inteligência do otimizador.

## RN-004 — Foco de Otimização é Minimizar Tokens

**Descrição:** O objetivo primário é reduzir consumo de tokens mantendo a qualidade das respostas.

**Contexto:** A métrica de sucesso é a relação entre redução de tokens e manutenção/melhoria de qualidade.

**Exceções:** Nenhuma. Tokens são a métrica principal.

## RN-005 — Limpeza Pós-Otimização

**Descrição:** Após análise e otimização, o agente otimizador deleta o arquivo `logs/exec.log` completo.

**Contexto:** Reduz sobrecarga de contexto nas próximas execuções do otimizador e evita análise redundante.

**Exceções:** Nenhuma. Arquivo é sempre deletado após processamento.

## RN-006 — Documentação de Otimizações

**Descrição:** Todas as otimizações realizadas (mudanças de prompts, ajustes de agentes) são documentadas em `doc/optimizations/<agent_id>-<timestamp>.md`.

**Contexto:** Rastreabilidade das mudanças e justificativas para análise histórica.

**Exceções:** Nenhuma. Toda otimização gera registro.

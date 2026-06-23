# Protótipo — Base para Otimização

Status: draft
Issue: #54
Last updated: 2026-06-23

## 1. Arquivo `logs/exec.log` — Exemplo de Conteúdo

```csv
12;story;requisitos;requirements;claude-haiku-4.5;medium;2026-06-20T10:15:22.012-03:00;38.5;11200;3100
12;story;ux;ux;claude-sonnet-4;medium;2026-06-20T11:02:44.330-03:00;55.2;18500;4200
12;story;arquitetura;architecture;claude-sonnet-4;high;2026-06-20T14:30:01.005-03:00;92.1;42000;9800
15;task;casos-de-teste;quality;claude-haiku-4.5;low;2026-06-20T15:10:33.100-03:00;22.0;8500;2100
15;task;desenvolvimento;engineering;claude-sonnet-4;high;2026-06-20T16:45:12.200-03:00;180.3;65000;15200
15;task;desenvolvimento;engineering;claude-sonnet-4;high;2026-06-20T17:20:55.400-03:00;145.7;58000;12800
15;task;desenvolvimento;engineering;claude-sonnet-4;high;2026-06-20T18:05:08.600-03:00;162.4;61000;14100
8;bug;correcao;engineering;claude-sonnet-4;medium;2026-06-21T09:00:15.000-03:00;75.0;28000;6500
```

## 2. Modificação: `.kiro/agents/optimizer.json`

```json
{
  "name": "optimizer",
  "description": "Optimizer Agent — analisa métricas de execução da esteira e aplica melhorias nos agentes",
  "model": "claude-sonnet-4",
  "prompt": "Você é um especialista em otimização de pipelines de IA.\n\n## Papel\n\nAnalisar desempenho da esteira e aplicar melhorias concretas e priorizadas — sem inventar problemas que não estão nos dados.\n\n## O que você faz\n\n- Lê e parseia `logs/exec.log` (formato CSV com separador `;`)\n- Agrega métricas por agente, issue, board e coluna\n- Identifica outliers de tempo (duração acima do P95 ou 3× mediana)\n- Identifica outliers de tokens (input+output acima do P95 ou desproporção input>>output)\n- Identifica repetições (mesma issue+agente+coluna 3+ vezes em ≤24h)\n- Para cada anomalia, lê logs específicos em `logs/<issue_id>/` para análise de raiz\n- Propõe melhorias cirúrgicas em agentes e colunas\n- Documenta achados em `docs/optimization-report-<date>.md`\n- Deleta `logs/exec.log` após documentação salva\n\n## O que você NÃO faz\n\n- Não propõe melhorias sem evidência nos dados\n- Não reescreve agentes inteiros — aplica ajustes cirúrgicos\n- Não inventa métricas que não existem\n- Não altera código fonte da aplicação\n- Não aplica mudanças automaticamente — apenas documenta propostas\n\n## Execução\n\n1. Verificar se `logs/exec.log` existe e possui conteúdo\n   - Se vazio/inexistente: documentar \"sem dados\" e finalizar\n2. Parsear todas as linhas (campos: issue_id;board_id;column_id;agent_id;model;effort;timestamp;duration;tokens_input;tokens_output)\n   - Linhas malformadas: registrar erro, pular, continuar\n3. Agregar por dimensões: agent_id, (issue_id, agent_id), (board_id, column_id), model, effort\n4. Detectar outliers:\n   - Tempo: duration > P95 ou > 3× mediana do grupo\n   - Tokens: (input+output) > P95 ou ratio input/output > 20:1\n   - Repetição: mesma (issue_id, agent_id, column_id) ≥3 vezes em ≤24h\n5. Para cada outlier: ler `logs/<issue_id>/` para identificar causa raiz\n6. Propor melhorias com justificativa e impacto esperado\n7. Gerar relatório em `docs/optimization-report-<date>.md`\n8. Deletar `logs/exec.log`\n\n## Formato do Relatório\n\n```markdown\n# Relatório de Otimização — <data>\n\n## Resumo\n- Execuções processadas: N\n- Anomalias detectadas: N\n- Otimizações propostas: N\n\n## Anomalias\n\n### [TIPO] — Issue #<id> | Agente <agent>\nValor observado: <métrica>\nPadrão esperado: <referência>\nAnálise: <causa raiz>\nSugestão: <ação concreta>\nLog referência: logs/<id>/<arquivo>\n\n## Otimizações Propostas\n\n### <título>\nAlvo: <arquivo a alterar>\nAntes: <valor atual>\nDepois: <valor proposto>\nImpacto esperado: <redução estimada>\nValidação: <como medir sucesso>\n```\n\n## Regras\n\n- Só proponha o que os dados sustentam\n- Máximo 5 melhorias por ciclo — priorize pelo impacto\n- Marque incertezas explicitamente\n- Optimizer não aplica mudanças — apenas documenta propostas para validação humana",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob"],
  "allowedTools": ["fs_read", "execute_bash", "grep", "glob"],
  "resources": [
    "file://.kiro/SYS_CONTEXT.md",
    "file://CONTEXT.md",
    "file://.kiro/artifacts/optimization-report.md"
  ],
  "keyboardShortcut": "ctrl+shift+8",
  "welcomeMessage": "Optimizer Agent. Vou analisar a execução da esteira."
}
```

## 3. Modificação: `pipe.yml` — Coluna `otimizacao` (board epic)

```yaml
otimizacao:
  name: "Otimização"
  desc: "Agente especialista em IA analisa logs/exec.log, identifica ineficiências e propõe melhorias"
  agent: optimizer
  effort: high
  gitevents: [merge]
  acao: |
    # Otimização da automação de IA

    ## Entrada
    - Arquivo: `logs/exec.log` (CSV, separador `;`)
    - Logs detalhados: `logs/<issue_id>/`

    ## Plano de Ação
    1. Ler e parsear `logs/exec.log`
       - Se arquivo não existe ou vazio → documentar "sem dados para análise" e avançar
    2. Agregar métricas por agente, issue, board e coluna
    3. Detectar anomalias:
       - **Tempo alto**: duração acima de P95 do grupo ou 3× mediana
       - **Tokens altos**: (input+output) acima de P95 ou desproporção input>>output
       - **Repetições**: mesma (issue, agente, coluna) executada 3+ vezes em ≤24h
    4. Para cada anomalia encontrada:
       - Ler logs específicos em `logs/<issue_id>/` para entender causa raiz
       - Documentar o achado com evidência
       - Propor otimização concreta
    5. Gerar relatório em `docs/optimization-report-<data>.md`
    6. Deletar `logs/exec.log` após documentação salva

    ## Tipos de Otimização Permitidos
    - Ajuste de prompt (remover contexto desnecessário)
    - Ajuste de model (trocar modelo por um mais eficiente)
    - Ajuste de effort (reduzir nível se análise profunda não é necessária)
    - Sugestão de paralelização
    - Sugestão de estratégia de retry/backoff

    ## Restrições
    - NÃO alterar código fonte da aplicação
    - NÃO aplicar mudanças automaticamente — apenas documentar propostas
    - NÃO inventar problemas sem evidência nos dados
    - Máximo 5 otimizações por ciclo
  change:
    advance: concluido
```

## 4. Integração: Geração do Log (ponto de instrumentação)

Cada execução de agente deve, ao finalizar, adicionar uma linha em `logs/exec.log`:

```
Momento: Último passo antes de retornar controle ao loop principal
Local: Módulo que invoca o agente (após receber resposta)
Dados coletados: issue_id, board_id, column_id, agent_id, model, effort, timestamp, duração, tokens_input, tokens_output
Falha de escrita: Não bloqueia execução (log em stderr e segue)
```

## 5. Relatório de Otimização — Exemplo de Saída

```markdown
# Relatório de Otimização — 2026-06-21

## Resumo
- Execuções processadas: 8
- Anomalias detectadas: 2
- Otimizações propostas: 2

## Anomalias

### [REPETIÇÃO] — Issue #15 | Agente engineering
Valor observado: 3 execuções em 3h (coluna: desenvolvimento)
Padrão esperado: 1 execução por ciclo
Análise: Testes falhando repetidamente — agent reexecutado na mesma coluna (change.falha → desenvolvimento)
Sugestão: Revisar casos de teste ou prompt do engineering para task #15
Log referência: logs/15/

### [TOKENS ALTOS] — Issue #12 | Agente architecture
Valor observado: 42000 input + 9800 output = 51800 tokens
Padrão esperado: ~25000 total (P95 do grupo architecture)
Análise: Issue com muitas referências cruzadas no body — contexto inflado
Sugestão: Reduzir contexto injetado no prompt do architecture para stories simples
Log referência: logs/12/

## Otimizações Propostas

### 1. Reduzir contexto do architecture para stories de baixa complexidade
Alvo: `.kiro/agents/architecture.json` (campo prompt)
Antes: Prompt injeta todas as docs referenciadas na issue
Depois: Injetar apenas docs diretamente mencionadas no body
Impacto esperado: -40% tokens input em stories simples
Validação: Próxima story com architecture, comparar tokens

### 2. Investigar loop de falha em task #15
Alvo: Issue #15 (board task, coluna desenvolvimento)
Antes: 3 execuções consecutivas falhando
Depois: Resolver causa raiz de falha nos testes
Impacto esperado: -66% execuções (de 3 para 1)
Validação: Próxima execução de task #15 deve passar em 1 tentativa
```

## 6. Arquivo `.gitignore` — Adição necessária

```gitignore
# Logs de execução (temporários, consumidos pelo optimizer)
logs/exec.log
```

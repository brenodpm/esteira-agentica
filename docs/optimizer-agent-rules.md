# Regras de Negócio — Agente Optimizer

Status: approved
Owner: requirements
Last updated: 2026-06-22

## Inputs

- `logs/exec.log` — arquivo agregado de execuções de agentes
- `logs/<issue_id>/` — diretórios com logs detalhados por issue

## RN-001 — Leitura e Parsing do Log

**Descrição:** O agente optimizer deve ler `logs/exec.log`, fazer parse de cada linha e carregar em memória.

**Contexto:** O arquivo é append-only, no formato CSV delimitado por `;`.

**Formato esperado:**
```
<issue_id>;<board_id>;<column_id>;<agent_id>;<model>;<effort>;<timestamp_iso>;<duration_seconds>;<tokens_input>;<tokens_output>
```

**Ações:**
- Se arquivo não existe ou está vazio → documentar "sem dados" e finalizar
- Se linha está malformada → registrar erro, pular linha, continuar
- Se token/duração são negativos → registrar, pular linha

## RN-002 — Identificação de Ineficiências

**Descrição:** O agente optimizer deve analisar o log e identificar 3 tipos de anomalias:

| Tipo | Indicador | Ação |
|------|-----------|------|
| **Tempo alto** | Outlier temporal (acima de P95 ou duração anormalmente longa para o contexto) | Documentar razão e sugerir paralela ou cache |
| **Custo alto** | Outlier de tokens (input+output acima de P95 ou proporção input>> output) | Documentar razão e sugerir prompt refinement |
| **Repetição** | Mesma issue, mesmo agente, mesma coluna, N vezes em curto período (interpretação do agente) | Documentar causa (blocked_by? erro?) e sugerir fix |

**Contexto:** Não há thresholds pré-definidos. O agente interpreta com base em padrões.

**Critério de "curto período":** Até 24 horas da execução anterior. Se > 3 execuções → anomalia.

## RN-003 — Sugestão de Análise Aprofundada

**Descrição:** Quando o agente identifica anomalia, deve sugerir análise dos logs específicos.

**Ações:**
- Se duração alta → ler `logs/<issue_id>/` para entender o fluxo (onde travou?)
- Se tokens altos → ler `logs/<issue_id>/` para análise de prompts e contexto
- Se repetição → verificar `/blocked_by` na issue, histórico de falhas

**Referência ao log detalhado:**
```
logs/<issue_id>/<timestamp>-<board>-<column>-<agent>.log
```

## RN-004 — Documentação de Achados

**Descrição:** Cada anomalia deve ser documentada de forma estruturada.

**Formato de documentação:**
```
## [TIPO] — Issue #<id> | Agente <agent_id>

**Data:** <timestamp>
**Anomalia:** <tipo>
**Valor observado:** <métrica> (ex: 5 minutos, 150k tokens)
**Padrão:** <histórico similar>

**Análise:**
- [motivo raiz — texto livre]

**Sugestão:**
- [ação concreta para otimizar]

**Referência de log:** logs/<issue_id>/
```

## RN-005 — Otimização do Agente/Prompt

**Descrição:** Com base na análise, propor melhorias no agente ou na coluna.

**Tipos de otimização:**
- **Prompt refinement** — remover contexto desnecessário, melhorar instrução
- **Model adjustment** — trocar de modelo (haiku → opus ou vice-versa)
- **Effort adjustment** — reduzir effort (high → medium) se não precisar de análise profunda
- **Parallelization** — dividir tarefa para executar em paralelo
- **Caching** — armazenar resultado intermediário para reuso

**Documentação de mudança:**
```
## Otimização Aplicada — Issue #<id>

**Antes:**
- Agent: <name>
- Model: <model>
- Effort: <effort>
- Tokens avg: <N>k

**Depois:**
- Agent: <name alterado?>
- Model: <model alterado?>
- Effort: <effort alterado?>
- Tokens expected: <N-M>k (redução esperada)

**Motivo:** [descrição curta]
**Validação:** [como testar a melhoria]
```

## RN-006 — Limpeza Pós-Análise

**Descrição:** Após documentar todas as otimizações, deletar `logs/exec.log`.

**Contexto:** Reduz contexto em ciclos futuros do optimizer.

**Ações:**
1. Documentação concluída e salva em arquivo persistente
2. Remover `logs/exec.log`
3. Registrar conclusão

**Condição de sucesso:** Arquivo deletado, nenhum log executado foi perdido (docs guardadas).

## RN-007 — Integração com Agente/Coluna

**Descrição:** Modificações propostas no agente ou coluna devem ser aplicáveis via `.kiro/agents/<agent>.json` ou `pipe.yml`.

**Exemplos:**
- Mudar `model` em `.kiro/agents/requirements.json`
- Mudar `effort` na coluna `requisitos` em `pipe.yml`
- Atualizar `prompt` ou `instructions` em `.kiro/agents/<agent>.json`

**Formato de aplicação:**
```json
{
  "id": "requirements",
  "model": "claude-haiku-4.5",
  "effort": "medium",
  "instructions": "..."
}
```

**Restrição:** Optimizer não aplica mudanças automaticamente. Apenas documenta. Um humano ou passo de validação aprova.

## Critérios de Sucesso

- [ ] Log parseado sem erros
- [ ] Todas as anomalias identificadas e documentadas
- [ ] Sugestões de otimização são viáveis e mensuráveis
- [ ] Arquivo `logs/exec.log` deletado após processamento
- [ ] Documentação salva em artefato persistente (issue ou arquivo)

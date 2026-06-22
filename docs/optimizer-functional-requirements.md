# Requisitos Funcionais — Agente Optimizer

Status: approved
Owner: requirements
Last updated: 2026-06-22

## Contexto

O agente optimizer é executado em coluna específica do board epic (a definir).
Responsável por análise contínua de ineficiências de execução e otimização de agentes/prompts.

## RF-001 — Acesso e Leitura do Log

**Descrição:** Agente deve acessar `logs/exec.log` e fazer parse das linhas.

**Dado que:** `logs/exec.log` existe e contém N linhas de execução
**Quando:** Agente inicia execução
**Então:** 
- Carrega todas as linhas em memória
- Estrutura dados: lista de dicts com campos parseados
- Valida campos (tipos, ranges)
- Registra quantidade de linhas válidas vs. inválidas

**Critério de aceitação:**
```gherkin
Cenário 1: Log válido
Dado "logs/exec.log" com 50 linhas bem-formadas
Quando parser lê o arquivo
Então retorna lista com 50 registros estruturados

Cenário 2: Log com erros
Dado "logs/exec.log" com 50 linhas (40 válidas, 10 com erro de formato)
Quando parser lê o arquivo
Então retorna lista com 40 registros + log de 10 erros

Cenário 3: Log ausente
Dado "logs/exec.log" não existe
Quando agente inicia
Então documenta "sem dados para análise" e finaliza graciosamente
```

## RF-002 — Agregação por Dimensão

**Descrição:** Agente deve agrupar execuções para análise de padrões.

**Agrupamentos:**
1. Por `agent_id` — tempo médio, tokens médios, volume
2. Por `(issue_id, agent_id)` — detecção de repetições
3. Por `(board_id, column_id)` — padrões por contexto
4. Por `model` — performance por modelo
5. Por `effort` — custos por nível

**Exemplo de agregação por agent:**
```python
{
  "requirements": {
    "executions": 15,
    "avg_duration": 45.2,
    "avg_tokens_input": 12000,
    "avg_tokens_output": 3500,
    "duration_p95": 120,
    "tokens_total_p95": 18500
  }
}
```

**Critério de aceitação:**
```gherkin
Cenário: Agregação correta
Dado 10 execuções do agent "engineering" com durações [10, 15, 20, 25, 30, 35, 40, 45, 50, 200]
Quando agrega por agent
Então calcula média = 47s, p95 ≈ 155s, outlier detectado: 200s
```

## RF-003 — Detecção de Outliers

**Descrição:** Identificar execuções anormais por tempo, tokens ou repetição.

### RF-003a — Outlier de Tempo
**Quando:** `duration > p95` da mesma dimensão OU `duration > 3× mediana local`
**Registra:** `{type: "time", issue_id, agent_id, duration, p95, desvio%}`

### RF-003b — Outlier de Tokens
**Quando:** `(tokens_input + tokens_output) > p95` OU `tokens_input >> tokens_output` (desproporção)
**Registra:** `{type: "tokens", issue_id, agent_id, input, output, ratio, p95}`

### RF-003c — Repetição de Execução
**Quando:** Mesma `(issue_id, agent_id)` executada 3+ vezes em ≤24h
**Registra:** `{type: "repetition", issue_id, agent_id, count, timespan_hours, last_attempt, first_attempt}`

**Critério de aceitação:**
```gherkin
Cenário: Detecção de tempo alto
Dado log com 5 execuções de "engineering" (30s, 35s, 32s, 28s, 600s)
Quando detecta outliers
Então identifica 600s como tempo alto (p95=35s, desvio=1614%)

Cenário: Detecção de tokens altos
Dado execução com input=50k, output=1k (taxa 50:1)
Quando detecta outliers
Então registra desproporção de input >> output

Cenário: Repetição detectada
Dado 3 execuções de (issue_id=108, agent_id=engineering) em 12 horas
Quando detecta repetições
Então registra anomalia de repetição, sugere análise de blocked_by
```

## RF-004 — Sugestão de Análise Específica

**Descrição:** Para cada outlier, sugerir qual log detalhado ler para raiz.

**Lógica:**
- Se outlier de **tempo** → sugerir `logs/<issue_id>/<timestamp>-*.log` mais longo
- Se outlier de **tokens** → sugerir `logs/<issue_id>/<timestamp>-*.log` com mais contexto
- Se outlier de **repetição** → sugerir ler issue history, `/blocked_by`, status GitHub

**Exemplo de sugestão:**
```
## Anomalia Detectada — Tempo Alto

Issue: #108 (task: desenvolvimento)
Agent: engineering
Duração observada: 5 minutos 22 segundos (p95: 2 min)

**Sugestão de análise:**
1. Ler: logs/108/20260622174520-task-desenvolvimento-engineering.log
   Procurar por: pontos de travamento, loops, retry de API
2. Verificar body da issue: há `/blocked_by`?
3. Histórico: mesma issue falhou antes?

**Possíveis causas:**
- Rate limit do GitHub (verifique try/except)
- Loop de retry sem backoff
- Contexto excessivo no prompt (muitas referências)
```

**Critério de aceitação:**
```gherkin
Cenário: Sugestão vinculada ao log
Dado outlier de tempo para issue #54
Quando gera sugestão
Então inclui caminho específico de log (logs/54/timestamp-*.log)
E inclui dicas de o que procurar
```

## RF-005 — Análise Preliminar de Raiz

**Descrição:** Agente deve ler logs específicos para confirmar causa antes de propor solução.

**Acesso a logs:**
- Ler `logs/<issue_id>/` (diretório com múltiplos arquivos por timestamp)
- Identificar última execução (timestamp mais recente)
- Extrair seções relevantes (erros, avisos, performance markers)

**Exemplo de extração:**
```
Issue #108 — últimas 3 execuções:
1. 2026-06-22T17:17:18 — 2 min 15 seg — OK
2. 2026-06-22T17:25:06 — 4 min 33 seg — OK com warnings
3. 2026-06-22T17:34:20 — 5 min 22 seg — OK com rate limit warnings × 3

Causa provável: Rate limiting do GitHub acumulado → backoff inadequado
```

**Critério de aceitação:**
```gherkin
Cenário: Identificação de raiz
Dado log detalhado com "rate limit" mencionado 3 vezes
Quando analisa
Então identifica causa provável = "rate limiting"
E sugere solução = "aumentar backoff exponencial"
```

## RF-006 — Proposição de Otimizações

**Descrição:** Com base em análise, propor mudanças concretas e viáveis.

**Tipos de mudança:**

| Mudança | Alvo | Arquivo | Exemplo |
|---------|------|---------|---------|
| Model | Agent | `.kiro/agents/<agent>.json` | `claude-opus-4` → `claude-haiku-4.5` |
| Effort | Coluna | `pipe.yml` | `high` → `medium` |
| Prompt | Agent | `.kiro/agents/<agent>.json` | Remover contexto desnecessário |
| Retry strategy | Agent | `.kiro/agents/<agent>.json` | Aumentar backoff |
| Parallelization | Coluna | `pipe.yml` | Executar múltiplas issues em paralelo |

**Validação de mudança:**
- Mudança deve ser aplicável (arquivo existe, estrutura válida)
- Mudança deve ser mensurável (puder validar resultado)
- Mudança não deve quebrar dependências

**Exemplo de proposição:**
```json
{
  "optimization_id": "opt-108-001",
  "issue_id": 108,
  "agent_id": "engineering",
  "type": "rate_limit_mitigation",
  "proposed_change": {
    "target": ".kiro/agents/engineering.json",
    "field": "retry_backoff_seconds",
    "current_value": 1,
    "proposed_value": 5,
    "rationale": "Log mostra rate limit warnings. Backoff atual insuficiente."
  },
  "expected_benefit": "Redução de 30% no tempo (de 5m22s para ~3m45s)",
  "validation": "Executar issue #108 novamente, comparar duração e tokens"
}
```

## RF-007 — Documentação de Resultado

**Descrição:** Agente deve documentar achados e otimizações em formato persistente.

**Saída esperada:**
- Arquivo ou issue no board com resumo de análise
- Lista de anomalias encontradas
- Lista de otimizações propostas
- Status de cada otimização (aplicada? pendente? descartada?)

**Formato de documentação (arquivo `docs/optimization-report-<date>.md`):**
```markdown
# Relatório de Otimização — 2026-06-22

## Resumo
- Execuções processadas: 150
- Anomalias detectadas: 8
- Otimizações propostas: 5

## Anomalias por Tipo

### Tempo Alto (3)
- Issue #108 — engineering — 5m22s (expected: 2m)
- [...]

### Tokens Altos (3)
- Issue #54 — requirements — 150k input (expected: 80k)
- [...]

### Repetições (2)
- Issue #75 — quality — 4 execuções em 18h
- [...]

## Otimizações Propostas

1. **Retry backoff para engineering**
   - Change: engineering.json backoff 1s → 5s
   - Expected: -30% em tempo
   - Status: Proposta

2. **Model downgrade para requirements**
   - Change: requirements.json model opus → haiku
   - Expected: -60% em tokens
   - Status: Proposta

[...]

## Próximos Passos
1. Validação manual de propostas
2. Aplicação em beta (issues new somente)
3. Coleta de métrica por 1 semana
4. Rollout completo
```

**Critério de aceitação:**
```gherkin
Cenário: Documentação completa
Dado 5 anomalias detectadas e 3 otimizações propostas
Quando gera relatório
Então inclui todas as anomalias, propostas e próximos passos
E arquivo é lido sem erros
```

## RF-008 — Limpeza Automática

**Descrição:** Após conclusão da análise, deletar `logs/exec.log`.

**Contexto:** Arquivo não é versionado, apenas para análise temporária.

**Critério de aceitação:**
```gherkin
Cenário: Limpeza bem-sucedida
Dado análise completa e documentação salva
Quando agente finaliza
Então `logs/exec.log` é deletado
E logs específicos em `logs/<issue_id>/` são preservados
```

## Critérios de Aceitação Gerais

- [ ] Log parseado corretamente
- [ ] Outliers detectados com acurácia ≥ 90%
- [ ] Análise de raiz não bloqueia execução (falha graciosamente)
- [ ] Propostas de otimização são mensuráveis e aplicáveis
- [ ] Relatório é documentado de forma clara
- [ ] Arquivo de log deletado após sucesso
- [ ] Falhas registradas em log sem bloquear ciclo

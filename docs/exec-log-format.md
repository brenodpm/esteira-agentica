# Formato de Log de Execução — `logs/exec.log`

Status: approved
Owner: requirements
Last updated: 2026-06-22

## Utilidade

Registrar execuções de agentes IA para análise contínua de ineficiências (tempo, tokens, repetições).
Fonte de dados exclusiva para o agente optimizer.

## Escopo

- **Inclui**: Execuções de agentes IA (análise, engenharia, QA, arquitetura, produto, etc.)
- **Exclui**: Ações mecânicas (sync, movimentação de cards, deleção de arquivos)

## Formato do Arquivo

Arquivo único: `logs/exec.log`
Cada linha adicionada ao final após cada execução de agente.

### Padrão por Linha

```
<issue_id>;<board_id>;<column_id>;<agent_id>;<model>;<effort>;<timestamp_iso>;<duration_seconds>;<tokens_input>;<tokens_output>
```

### Exemplo

```
54;story;requisitos;requirements;claude-haiku-4.5;medium;2026-06-22T17:44:22.012-03:00;45;12000;3500
108;task;desenvolvimento;engineering;claude-opus-4;high;2026-06-22T17:45:10.105-03:00;120;35000;8200
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `issue_id` | int | ID da issue executada |
| `board_id` | string | ID do board (story, task, epic, bug, debito, incidente) |
| `column_id` | string | ID da coluna onde a issue estava |
| `agent_id` | string | ID do agente executor (requirements, engineering, quality, etc.) |
| `model` | string | Modelo LLM usado (claude-haiku-4.5, claude-opus-4, etc.) |
| `effort` | string | Nível de esforço: low, medium, high |
| `timestamp_iso` | string | ISO 8601 com timezone (ex: 2026-06-22T17:44:22.012-03:00) |
| `duration_seconds` | float | Tempo total de execução em segundos (≥0) |
| `tokens_input` | int | Tokens de entrada usados (≥0) |
| `tokens_output` | int | Tokens de saída produzidos (≥0) |

## Regras de Escrita

1. **Append-only**: Sempre adicionar ao final, nunca sobrescrever linhas
2. **Separador**: `;` (ponto-e-vírgula, sem espaços)
3. **Sem cabeçalho**: Começa direto com dados
4. **Sem quebras vazias**: Cada linha é uma execução
5. **Encoding**: UTF-8
6. **Timestamps**: ISO 8601 com timezone do sistema

## Integração com Esteira

### Geração
- **Quem**: Cada agente ao finalizar execução
- **Quando**: Último passo antes de retornar controle
- **Falha de escrita**: Não bloqueia execução, registra error em log padrão

### Consumo
- **Quem**: Agente optimizer (coluna "otimizacao" do board epic)
- **Quando**: Acionado manualmente ou por ciclo (a definir)
- **Processamento**: Lê arquivo, analisa, documenta, deleta arquivo

## Limpeza

Após análise completa, o arquivo `logs/exec.log` é **deletado** para reduzir contexto em ciclos futuros.
Não há histórico persistido — apenas logs específicos por issue em `logs/<issue_id>/`.

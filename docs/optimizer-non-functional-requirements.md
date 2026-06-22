# Requisitos Não-Funcionais — Agente Optimizer

Status: approved
Owner: requirements
Last updated: 2026-06-22

## Inputs

- `logs/exec.log` — arquivo agregado de execuções
- `logs/<issue_id>/` — diretórios com logs detalhados

## Performance

| Métrica | Target | Justificativa |
|---------|--------|---------------|
| Parse de 1000 linhas | ≤ 5s | Não bloqueia execução, cache em memória |
| Cálculo de aggregados | ≤ 10s | Operações O(n) com pandas/numpy |
| Detecção de outliers | ≤ 15s | Cálculo de percentis e desvios |
| Leitura de 50 logs detalhados | ≤ 30s | I/O limitado, processamento paralelo permitido |
| Geração de relatório | ≤ 5s | Markdown rendering simples |
| **Total esperado por execução** | **≤ 60s** | Não bloqueia ciclo de 5 minutos |

## Segurança

- [ ] Arquivo `logs/exec.log` não versionado (`.gitignore`)
- [ ] Logs específicos em `logs/<issue_id>/` não contêm secrets/tokens
- [ ] Parsing tolerante a valores inesperados (não causa RCE/injection)
- [ ] Sem acesso a arquivos fora de `logs/` e `docs/`
- [ ] Relatório não expõe prompts inteiros (apenas referências)

## Escalabilidade

| Cenário | Capacidade | Notas |
|---------|-----------|-------|
| Log pequeno (< 100 linhas) | Trata sem problema | Caso mais comum |
| Log médio (100-1000 linhas) | Trata com ~30s | Uma semana de operação típica |
| Log grande (> 1000 linhas) | Trata com cuidado | Fallback: processar em chunks |
| Arquivo que cresce enquanto processa | Snapshot no início | Ler uma vez, processar versão estática |

**Estratégia de chunks (se necessário):**
- Se > 1000 linhas, dividir em blocos de 500
- Processar sequencialmente, manter agregados em arquivo temporário
- Combinar resultados no final

## Disponibilidade

- [ ] Falha de leitura do log → log erro, finalizar graciosamente (sem crash)
- [ ] Log vazio → documentar "sem dados", não falhar
- [ ] Linha malformada → registrar erro, pular linha, continuar
- [ ] Arquivo não encontrado → criar vazio ou documentar e finalizar
- [ ] Falta de permissão em `logs/` → registrar erro, sugerir manualmente

## Qualidade de Dados

| Aspecto | Validação | Ação se falhar |
|---------|-----------|----------------|
| Formato de linha | Deve ter 10 campos separados por `;` | Pular linha, registrar erro |
| `issue_id` | Deve ser int ≥ 1 | Pular linha |
| `board_id` | Deve estar em lista whitelist | Pular linha (warning) |
| `column_id` | String não-vazia | Pular linha |
| `agent_id` | String não-vazia | Pular linha |
| `model` | String não-vazia | Pular linha |
| `effort` | low, medium, high | Pular linha (warning) |
| `timestamp` | ISO 8601 válido | Pular linha |
| `duration_seconds` | Float ≥ 0 | Pular linha |
| `tokens_input`, `tokens_output` | Int ≥ 0 | Pular linha |

## Confiabilidade

- [ ] Nenhuma mutação de estado externo até finalizar com sucesso
- [ ] Arquivo `logs/exec.log` só deletado após documentação estar salva
- [ ] Rollback em caso de erro: logs/exec.log preservado, relatório descartado
- [ ] Rastreabilidade: cada análise registra timestamp inicial/final e status

## Usabilidade (para próximas iterações)

- [ ] Relatório em formato legível (markdown, JSON ou HTML)
- [ ] Sugestões com justificativa clara (não apenas valores numéricos)
- [ ] Exemplos de como aplicar mudança proposta (snippets JSON)

## Observabilidade

- [ ] Cada execução gera log estruturado: `logs/2026-06-22-optimizer.log`
- [ ] Log contém: timestamp, linhas processadas, outliers encontrados, propostas geradas
- [ ] Erros registrados com stack trace (não imprime em stdout)
- [ ] Métricas: tempo total, linhas inválidas, outliers, propostas

## Compatibilidade

- [ ] Python 3.7+ (projeto usa 3.14)
- [ ] Sem deps adicionais se possível (usar stdlib: csv, json, statistics, pathlib)
- [ ] Se necessário, usar pandas/numpy (já no projeto)

## Limites e Quotas

| Limite | Valor | Razão |
|--------|-------|-------|
| Max linhas por análise | 10.000 | Evitar OOM em ambiente limitado |
| Max tamanho do relatório | 1 MB | Arquivo legível e editável |
| Max logs detalhados para ler | 50 | Tempo de I/O controlado |
| Retenção de logs/<issue_id>/ | Indefinida | Histórico preservado |
| Retenção de logs/exec.log | Temporária (deletado após análise) | Reduzir contexto |

## Monitoramento

Métricas para observar em produção:
- Taxa de linhas válidas vs. inválidas
- Tempo médio de análise por log
- Quantidade de outliers detectados por tipo
- Taxa de sucesso vs. falha

## Conformidade

- [ ] LGPD: Não armazena dados pessoais além de issue_id e timestamps
- [ ] Integridade: Log é append-only, sem mutação de registros anteriores
- [ ] Auditoria: Cada análise deixa trilha em relatório persistido

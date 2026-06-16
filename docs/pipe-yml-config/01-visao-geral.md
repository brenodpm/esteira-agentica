# Visão Geral do pipe.yml

O `pipe.yml` é o arquivo de configuração central da Esteira Agêntica. Toda a estrutura de boards, colunas, fluxos de trabalho e configurações de agentes é definida nele.

**O pipe.yml é mandatório**: qualquer alteração nele sobrescreve a estrutura local e remota na próxima execução da esteira.

## Estrutura Geral

```yaml
pipe:                    # Configurações globais do agente
effort:                  # Mapeamento de níveis de effort para models
doc:                     # Caminho da documentação
git:                     # Configurações de repositório e gitflows
boards:                  # Definição de todos os boards do projeto
```

## Resolução de Precedência

A esteira segue uma ordem de resolução para determinar qual configuração usar:

1. **Arquivo `.kiro/agents/<nome>.json`** — padrões do agente específico
2. **Coluna `effort` em `pipe.yml`** — sobrescreve effort do agente
3. **Tag `/effort` na issue** — sobrescreve model e effort (requer `allow-overwrite: true` na coluna)

## Próximos Passos

- [02-configuracao-global.md](02-configuracao-global.md) — Entenda as opções globais
- [03-gitflows.md](03-gitflows.md) — Configure seus fluxos de branch
- [04-boards-e-colunas.md](04-boards-e-colunas.md) — Crie e organize seus boards
- [05-agentes-e-esforco.md](05-agentes-e-esforco.md) — Defina agentes e níveis de esforço
- [06-exemplos-praticos.md](06-exemplos-praticos.md) — Explore casos de uso comuns

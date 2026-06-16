# Documentação Completa do pipe.yml

Guias passo-a-passo e referência técnica para configurar a Esteira Agêntica.

## 📑 Índice

1. **[Visão Geral](01-visao-geral.md)** — O que é pipe.yml, estrutura base, próximos passos
2. **[Configuração Global](02-configuracao-global.md)** — Timeout, sleeptime, TTL logs, caminho de docs
3. **[Git Flows](03-gitflows.md)** — Como criar branches (feature, epic, hotfix), resolução de prefixos dinâmicos
4. **[Boards e Colunas](04-boards-e-colunas.md)** — Criar workflows, transições, eventos git
5. **[Agentes e Esforço](05-agentes-e-esforco.md)** — Atribuir agentes, controlar profundidade de análise
6. **[Exemplos Práticos](06-exemplos-praticos.md)** — 6 cenários reais (novo board, customizar effort, gitflow, validação, etc)

## 🚀 Comece Aqui

### Para Iniciantes
Leia nesta ordem:
1. Visão Geral → entenda a estrutura
2. Configuração Global → setup básico
3. Boards e Colunas → defina seu primeiro workflow
4. Git Flows → configure branches

### Para Usuários Avançados
Vá direto para:
- Exemplos Práticos → veja casos de uso semelhantes ao seu
- Agentes e Esforço → fine-tune desempenho vs custo

## 💡 Casos de Uso Comuns

| Caso | Documento |
|------|-----------|
| "Quero criar um novo board" | [Exemplos Práticos - Cenário 1](06-exemplos-praticos.md#cenário-1-adicionar-um-novo-board) |
| "Como customizar níveis de effort?" | [Exemplos Práticos - Cenário 2](06-exemplos-praticos.md#cenário-2-customizar-níveis-de-effort) |
| "Quero um gitflow customizado" | [Exemplos Práticos - Cenário 3](06-exemplos-praticos.md#cenário-3-criar-um-gitflow-customizado) |
| "Como usar validação humana?" | [Exemplos Práticos - Cenário 4](06-exemplos-praticos.md#cenário-4-board-com-validação-humana) |
| "Como fazer um épico esperar todas as stories?" | [Exemplos Práticos - Cenário 5](06-exemplos-praticos.md#cenário-5-dependência-entre-boards) |
| "Posso variar effort por issue?" | [Exemplos Práticos - Cenário 6](06-exemplos-praticos.md#cenário-6-esforço-variável-por-issue) |

## 🔗 Referência Rápida

### Estrutura Base

```yaml
pipe:                    # Configurações globais
effort:                  # Mapeamento de esforço
doc:                     # Caminho de documentação
git:                     # Setup de repositório e gitflows
boards:                  # Definição de boards e workflows
```

### Resolução de Precedência (Effort)

1. `.kiro/agents/<nome>.json` — padrão do agente
2. `pipe.yml` → coluna `effort` — sobrescreve agente
3. Issue `/effort` tag — sobrescreve tudo (se `allow-overwrite: true`)

### Prioridade de Processamento

- Boards com `priority: 0` são processados primeiro
- Dentro de um board, issues são processadas em ordem (ou paralelas se `parallel: true`)

## 🎓 Aprenda Pelos Exemplos

**Quer configurar...**

- Uma esteira minimalista? → Veja Visão Geral
- Um fluxo SCRUM? → Veja Exemplos Práticos
- Uma esteira com hotfixes prioritários? → Veja Git Flows + Cenário 3
- Validação humana entre agentes? → Veja Cenário 4
- Épicos com dependências? → Veja Cenário 5

## ✅ Checklist: Validar seu pipe.yml

- [ ] Todos os boards têm `name` e `todo`
- [ ] Colunas iniciais correspondem ao `todo`
- [ ] Cada coluna com `agent` tem `acao` definida
- [ ] Transições de `change` usam IDs que existem
- [ ] Gitflows em `flow` estão definidos em `git.flow`
- [ ] `priority` dos boards é incremental
- [ ] `effort` levels têm `model` e `effort`
- [ ] Nomes de coluna são curtos (compatível com GitHub)

## 📞 Suporte

Se ainda tiver dúvidas:
- Releia o documento do seu cenário
- Confira o checklist acima
- Procure por "Impacto:" nos docs (explica o efeito das configurações)

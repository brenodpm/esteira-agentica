# User Story

## Utilidade

Define uma unidade de entrega de valor do ponto de vista do usuário. Contém regras de negócio e critérios de aceitação testáveis. Serve tanto como documentação de referência quanto como issue de movimentação no board story.

## Layout de Documentação

```markdown
# US — <título>

Status: draft | approved | deprecated
Owner: product
Last updated: YYYY-MM-DD

## Inputs
- <arquivos utilizados>

## Descrição
Como <tipo de usuário>
Quero <ação>
Para <objetivo>

## Regras de negócio
- ...

## Critérios de aceitação
- Dado <contexto>, quando <ação>, então <resultado>
- ...

## Não objetivos
- ...
```

## Layout de Issue

```markdown
# <título da user story>

Como <tipo de usuário>
Quero <ação>
Para <objetivo>

## Regras de negócio
- ...

## Critérios de aceitação
- Dado <contexto>, quando <ação>, então <resultado>
- ...

## Não objetivos
- ...

<adicionar tags aqui>
```

## Tags a serem usadas na issue

```
/blocked_by <issue-id>     # opcional — id das issues que bloqueiam a execução desta
/need_human                # opcional — indica que necessita intervenção humana
/branch <nome>             # branch de execução da issue atual
/parent_branch <nome>      # condicional — branch da issue pai (quando originada de outra issue)
/effort [ low | medium | high ]  # opcional — sobrescreve model/effort (requer allow-overwrite na coluna)
```

## Caminho do Arquivo

`doc/product/<slug-epic>/stories/<slug-story>.md`

## Board

`story` — coluna `backlog`

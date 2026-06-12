# Task

## Utilidade

Define uma unidade mínima de trabalho executável pela engenharia. Contém escopo, critério de aceite e classificação de effort para determinar o nível de modelo a ser utilizado na implementação.

## Layout de Issue

```markdown
# <título da task>

effort: low | medium | high

## User Story
<referência à story relacionada>

## Descrição
<o que deve ser feito — objetivo e direto>

## Escopo técnico
<o que está incluso>

## Fora de escopo
<limites claros>

## Critério de aceite
- Implementação segue arquitetura
- Código cobre cenário descrito
- Testes unitários criados
- Sem quebra de funcionalidades existentes

<adicionar tags aqui>
```

## Board

`task` — coluna `backlog`

## Tags a serem usadas na issue

```
/blocked_by <issue-id>     # opcional — id das issues que bloqueiam a execução desta
/need_human                # opcional — indica que necessita intervenção humana
/branch <nome>             # branch de execução da issue atual
/parent_branch <nome>      # condicional — branch da issue pai (quando originada de outra issue)
/effort [ low | medium | high ]  # opcional — sobrescreve model/effort (requer allow-overwrite na coluna)
```

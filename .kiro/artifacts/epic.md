# Epic

## Utilidade

Solicitação de origem humana que inicia o ciclo completo da esteira. É o nível mais alto de trabalho — acima de user stories. Passa por análise de negócio, planejamento, implementação e publicação.

## Layout de Issue

```markdown
# <título do épico>

## Descrição
<o que o humano precisa>

## Contexto
<por que este épico existe>

## Resultado esperado
<o que se espera ao final>

<adicionar tags aqui>
```

## Board

`epic` — coluna `backlog`

## Tags a serem usadas na issue

```
/blocked_by <issue-id>     # opcional — id das issues que bloqueiam a execução desta
/need_human                # opcional — indica que necessita intervenção humana
/branch <nome>             # branch de execução da issue atual
/parent_branch <nome>      # condicional — branch da issue pai (quando originada de outra issue)
/effort [ low | medium | high ]  # opcional — sobrescreve model/effort (requer allow-overwrite na coluna)
```

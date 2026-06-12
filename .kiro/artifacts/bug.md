# Bug

## Utilidade

Documenta um defeito encontrado durante execução de testes, com reprodução clara e classificação de severidade. Serve como issue de movimentação no board bug.

## Layout de Issue

```markdown
# <título do bug>

## Descrição
<problema objetivo>

## Passos para reproduzir
1. ...

## Resultado esperado
...

## Resultado obtido
...

## Severidade
critical | high | medium | low

## Tipo de violação
requisito | arquitetura | regressão

## Referências
- <caso de teste>
- <task relacionada>

<adicionar tags aqui>
```

## Board

`bug` — coluna `backlog`

## Tags a serem usadas na issue

```
/blocked_by <issue-id>     # opcional — id das issues que bloqueiam a execução desta
/need_human                # opcional — indica que necessita intervenção humana
/branch <nome>             # branch de execução da issue atual
/parent_branch <nome>      # condicional — branch da issue pai (quando originada de outra issue)
/effort [ low | medium | high ]  # opcional — sobrescreve model/effort (requer allow-overwrite na coluna)
```

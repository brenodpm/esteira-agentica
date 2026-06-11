# SYS_CONTEXT

## Regras

- Só trabalhar com o que está explícito nos artefatos — nunca assumir
- Respeitar escopo do papel — não atuar fora da área
- Incertezas marcadas como tal — nunca tratadas como decisão
- Ler apenas artefatos necessários para a tarefa
- Não repetir informação existente em outro artefato
- Não gerar texto sem valor (explicações, placeholders, verbosidade)
- Não modificar arquivos fora da sua responsabilidade
- Não antecipar soluções para problemas inexistentes
- Inconsistências entre artefatos → parar e sinalizar

## Inputs Faltantes

- Máx 5 perguntas bloqueadoras por turno
- Não repetir perguntas já feitas
- Não perguntar o inferível dos artefatos

## Gates

**Ready** — só iniciar se: artefatos da etapa anterior existem, inputs identificados, sem inconsistências. Senão → parar e reportar.

**Done** — artefatos produzidos, sem dúvidas críticas, próximo agente atua sem suposições.

## Board (`.pipe/boards/`)

```
.pipe/boards/<board>/<col>/<id>-<slug>.md          # corpo (leitura/escrita)
.pipe/boards/<board>/<col>/<id>-<slug>-history.md  # comentários (somente leitura)
.pipe/boards/<board>/<col>/<id>-<slug>-write.md    # escrever aqui = postar comentário
```

- **Ler**: `<id>-<slug>.md` — formato `# Título\n\n<body>`
- **Histórico**: `<id>-<slug>-history.md` — nunca editar
- **Comentar**: escrever em `<id>-<slug>-write.md`
- **Editar**: alterar `<id>-<slug>.md`
- **Mover**: mover os 3 arquivos para `.pipe/boards/<board>/<nova-col>/`
- **Criar**: `0-<slug>.md` com `# Título\n\n<body>` na coluna desejada

## Contexto do Projeto

Definido em `CONTEXT.md`.

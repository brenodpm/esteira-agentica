Status: in-progress
Owner: architecture-agent
Last updated: 2026-05-31

## Inputs
- docs/02-architecture/overview.md
- docs/00-product/vision.md
- docs/00-product/migration-plan.md

## Descrição

Após a conclusão e estabilização da v1, este projeto deve passar a ser desenvolvido usando a própria esteira que construiu. Isso requer um plano de migração que cubra:

- Importar o backlog atual para o formato gerenciado pela esteira
- Configurar o projeto `esteira-agentica` como projeto-alvo da própria esteira
- Validar o ciclo completo (ideia → entrega) usando a esteira no próprio repositório
- Identificar e resolver inconsistências que só aparecem quando a esteira opera sobre si mesma

> **Incerteza:** a migração pode expor limitações da v1 não previstas. O plano deve ser incremental e reversível.

## Impacto

Sem isso, o projeto continua sendo desenvolvido manualmente — contradiz a proposta de valor central do produto.

## Responsável pela resolução

architecture-agent (plano) + engineering-agent (execução)

## Bloqueia etapa?

Não — pós v1.

## Progresso (2026-05-28)

### Concluído
- [x] `docs/02-architecture/artifact-map.md` criado — contrato de artefatos por agente
- [x] `.kiro/agents/*.json` otimizados — fs_write habilitado, contextFiles injetados, paths explícitos
- [x] `docs/02-architecture/adr-007-kiro-agents-como-runtime.md` — decisão arquitetural registrada
- [x] `docs/02-architecture/overview.md` atualizado — componente `.kiro/agents/` formalizado
- [x] `docs/00-product/migration-plan.md` atualizado — pré-requisitos técnicos detalhados

## Progresso (2026-05-31)

### Concluído
- [x] `esteira.yml` como config base — `src/config/loader.py` reescrito para YAML (ADR-008)
- [x] `docs/02-architecture/overview.md` atualizado com `esteira.yml` como config central
- [x] `docs/00-product/migration-plan.md` atualizado com `esteira.yml` como config central
- [x] Agentes `.kiro/agents/` atualizados com `esteira.yml` em `contextFiles`
- [x] `README.md` público criado com instruções de uso

### Próximos passos
- [ ] Criar issues no GitHub para as próximas features usando a esteira
- [ ] Executar primeiro ciclo completo (product → requirements → architecture → tech-lead → engineering → quality) usando os agentes Kiro
- [ ] Registrar fricções encontradas como débitos para evolução da esteira
- [ ] Validar que o orquestrador consegue ler `artifact-map.md` para validar pré/pós-condições

## Changes
- Status alterado de `open` para `in-progress` (2026-05-28)
- Progresso atualizado (2026-05-31): esteira.yml como config base implementado, agentes otimizados, README criado

Status: resolved
Owner: product-agent
Last updated: 2026-05-28

## Inputs
- docs/00-product/vision.md

## Descrição

O repositório é público. Ao final de cada ciclo (equivalente a uma sprint/milestone), a documentação pública deve ser atualizada para refletir o estado atual do projeto — partindo do README.

Escopo esperado:
- README como ponto de entrada: o que é, como instalar, como usar, como contribuir
- Atualização incremental a cada ciclo — não reescrever do zero, evoluir
- Linguagem acessível para quem encontra o projeto sem contexto prévio

A atualização do README deve ser uma tarefa obrigatória no encerramento de cada milestone, executada pelo engineering-agent ou operations-agent com revisão humana.

> **Incerteza:** o formato ideal do README e o nível de detalhe adequado para cada ciclo precisam ser definidos quando a v1 estiver próxima de ser entregue.

## Impacto

Sem isso, o projeto público fica desatualizado e inutilizável por terceiros — contradiz o objetivo de ser adotável por outros times.

## Responsável pela resolução

product-agent (definir estrutura do README) + engineering-agent (executar a cada ciclo)

## Bloqueia etapa?

Não — começa a ser relevante na entrega da v1.

## Resolução
- Estrutura do README definida no `docs/00-product/migration-plan.md` (seção de adoção pública)
- Atualização incremental do README delegada ao engineering-agent a cada milestone
- Épico de Adoção e Migração formaliza essa responsabilidade em `docs/00-product/epicos.md`
- Data: 2026-05-28
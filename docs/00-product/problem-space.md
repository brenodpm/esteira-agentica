Status: approved
Owner: product-agent
Last updated: 2026-05-14T21:51:00-03:00

## Inputs
- statup.md

## Contexto
Existe uma estrutura robusta de esteira de desenvolvimento com agentes de IA simulando papéis como Produto, Requisitos, UX, Arquitetura, Qualidade e Engenharia. Porém, toda a orquestração entre agentes é feita manualmente pelo usuário.

## Problemas
- **[CRÍTICO]** Sem controle de consumo de tokens: agentes podem processar contexto desnecessário, repetir informações já existentes e gerar saídas verbosas, elevando o custo de forma invisível
- O humano atua como orquestrador e gerenciador de tarefas, sendo o principal gargalo do processo
- Não há integração automática com sistemas de gestão de tarefas (Kanban, Scrum, etc.)
- Não há integração automática com repositórios git
- Não há coleta de métricas de execução (tempo, custo em tokens, retrabalho, delírios de IA)
- O sistema exige presença física/direta do usuário para operar

## Impacto
- Custo crescente e imprevisível com tokens a cada execução
- Velocidade de entrega limitada pela disponibilidade e atenção do humano
- Ausência de rastreabilidade e auditoria do processo
- Impossibilidade de escalar ou rodar o processo de forma autônoma
- Qualidade das execuções de IA não é mensurável

## Changes
- Problema de custo em tokens adicionado como CRÍTICO
- Impacto de custo promovido para primeiro item
- Motivo: alinhamento com prioridade definida pelo usuário

## Oportunidade
A maturidade atual das ferramentas de IA CLI (como Kiro) e de gestão de tarefas gratuitas permite construir uma camada de orquestração automatizada que mantém o humano apenas nos gates de aprovação, eliminando o gargalo sem abrir mão do controle.

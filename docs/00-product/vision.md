Status: approved
Owner: product-agent
Last updated: 2026-05-14T21:51:00-03:00

## Inputs
- statup.md

## Problema
Esteiras de desenvolvimento multi-agente existem, mas o acionamento dos agentes é manual, tornando o humano o gargalo como gerenciador de tarefas e orquestrador.

## Solução
Uma esteira agêntica automatizada que orquestra agentes de IA em papéis bem definidos, integrada a um sistema de gestão de tarefas e ao git, com aprovação humana em cada etapa e coleta de métricas de execução.

## Público-alvo
Desenvolvedores e times de engenharia que utilizam esteiras de desenvolvimento com agentes de IA e querem eliminar a dependência do humano como orquestrador.

## Proposta de valor
Automatizar a orquestração entre agentes de IA com foco prioritário em minimizar o consumo de tokens — cada agente lê apenas o necessário, evita reprocessamento e produz saídas enxutas — mantendo controle humano nos gates de aprovação e rodando com ferramentas gratuitas.

## Métricas de sucesso
- **[PRIORIDADE 1]** Custo total em tokens por feature entregue (meta: minimizar)
- **[PRIORIDADE 1]** Custo em tokens por agente/etapa (identificar agentes mais caros)
- Redução do tempo de intervenção manual do usuário na orquestração
- Taxa de retrabalho por agente
- Número de "delírios de IA" detectados e bloqueados
- Ciclo completo (ideia → entrega) executado sem interação direta com a máquina

## Changes
- Proposta de valor atualizada para destacar minimização de tokens como prioridade central
- Métricas de custo em tokens promovidas para PRIORIDADE 1
- Motivo: alinhamento com diretriz do usuário

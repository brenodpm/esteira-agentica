# Problem Space — Horário de Funcionamento

Status: draft
Owner: product
Last updated: 2026-06-17

## Inputs
- Issue #114 - Horário de funcionamento
- Código atual do loop principal
- Configuração `pipe.agent.sleeptime`

## Contexto
A esteira agêntica opera com um loop contínuo que verifica tarefas a cada intervalo configurado (`sleeptime`). Atualmente não há controle sobre quando este loop pode executar, rodando 24/7 independente de supervisão.

## Problemas
- Consumo descontrolado de tokens fora do horário comercial
- Execução sem supervisão pode gerar panes não detectadas
- Falta de flexibilidade para ajustar operação a diferentes fusos horários
- Impossibilidade de pausar automaticamente em feriados ou períodos específicos
- Risco financeiro por consumo não planejado de APIs pagas

## Impacto
- Custos elevados e imprevisíveis de tokens/API calls
- Risco operacional por execução sem monitoramento
- Falta de controle administrativo sobre recursos computacionais

## Oportunidade
Implementar controle temporal simples e eficaz que se integre ao loop existente, mantendo a arquitetura atual mas adicionando verificações de horário antes da execução de tarefas.

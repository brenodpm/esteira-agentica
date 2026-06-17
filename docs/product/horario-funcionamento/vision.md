# Vision — Horário de Funcionamento

Status: draft
Owner: product
Last updated: 2026-06-17

## Inputs
- Issue #114 - Horário de funcionamento
- Análise do código `src/__main__.py`
- Configuração atual `pipe.yml`

## Problema
A esteira agêntica roda continuamente sem controle de horários, podendo consumir tokens de forma descontrolada em momentos sem supervisão (noites, fins de semana, feriados), causando panes financeiras e operacionais.

## Solução
Sistema de configuração de horário de funcionamento que permite definir janelas temporais de operação da esteira, incluindo fuso horário, horários diários, dias da semana e feriados específicos.

## Público-alvo
Administradores da esteira agêntica que precisam controlar custos e supervisionar operações.

## Proposta de valor
Controle preciso sobre quando a esteira pode operar, evitando consumo desnecessário de tokens e garantindo supervisão adequada das operações.

## Métricas de sucesso
- Redução de custos por não execução fora do horário configurado
- Zero execuções em horários/dias bloqueados
- Configuração flexível atendendo diferentes fusos e calendários

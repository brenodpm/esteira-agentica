# Épicos — Horário de Funcionamento

Status: draft
Owner: product
Last updated: 2026-06-17

## Inputs
- Vision e problem space do épico
- Análise da arquitetura atual da esteira

## Épico: Configuração de Horário

**Objetivo:** Permitir configuração flexível de janelas de funcionamento da esteira
**Escopo:** 
- Configuração de fuso horário no `pipe.yml`
- Definição de horário de início e fim diário
- Seleção de dias da semana ativos
- Lista de feriados para bloqueio
- Validação das configurações

**Fora de escopo:**
- Interface gráfica para configuração
- Configurações por board específico
- Horários diferentes por dia da semana
- Integração com calendários externos

## Épico: Motor de Verificação

**Objetivo:** Implementar verificação de horário no loop principal da esteira
**Escopo:**
- Função de verificação se está em horário permitido
- Integração no loop principal antes da execução de tarefas
- Log de bloqueios por horário
- Tratamento de edge cases (mudança de horário, feriados)

**Fora de escopo:**
- Alteração da arquitetura do loop principal
- Cache de verificações de horário
- Notificações de bloqueio
- Pausa/resume manual de operações

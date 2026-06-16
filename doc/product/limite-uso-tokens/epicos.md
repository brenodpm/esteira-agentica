# Épicos — Limite de uso de tokens

Status: draft
Owner: product
Last updated: 2025-06-16

## Inputs
- Issue #55 - Limite de uso de tokens
- vision.md
- problem-space.md

## Épico: Configuração de Limites

**Objetivo:** Permitir configurar limites de consumo de tokens por dia, mês e projeto
**Escopo:** 
- Adição de propriedades de configuração no pipe.yml
- Validação dos valores configurados
- Documentação das configurações
**Fora de escopo:** Interface gráfica para configuração

## Épico: Monitoramento de Consumo

**Objetivo:** Rastrear o consumo atual de tokens e persistir o estado
**Escopo:**
- Estrutura de dados para registro de consumo
- Atualização automática de contadores
- Reset automático por período
- Sincronização com dados da conta via kiro-cli
**Fora de escopo:** Relatórios históricos detalhados

## Épico: Controle de Execução

**Objetivo:** Impedir execução de agentes quando limites são atingidos
**Escopo:**
- Verificação de limites antes da execução
- Bloqueio automático quando necessário
- Delay até próximo período permitido
**Fora de escopo:** Notificações externas ou alertas

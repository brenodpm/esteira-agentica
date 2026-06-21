# Vision — Mudança de Arquitetura

Status: draft
Owner: product
Last updated: 2026-06-21

## Inputs
- Issue epic/131-mudanca_de_arquitetura.md
- Análise da estrutura atual do projeto

## Problema
A arquitetura atual do projeto está monolítica, limitando a extensibilidade para novas integrações. O sistema atualmente só suporta GitHub Projects V2 como board, não possui integração com email, mensagens instantâneas ou outros sistemas de IA generativa, e as configurações estão acopladas ao diretório `.kiro/` específico de uma empresa de IA.

## Solução
Migrar para arquitetura hexagonal, transformando os componentes existentes em adapters de ports bem definidos. Isso permitirá adicionar facilmente novos adapters para diferentes boards online, provedores de IA, sistemas de comunicação e outras integrações, mantendo o core do negócio isolado das dependências externas.

## Público-alvo
- Desenvolvedores que mantêm esteiras agênticas
- Equipes que querem integrar a esteira com diferentes ferramentas
- Comunidade open source que deseja criar adapters personalizados

## Proposta de valor
- Extensibilidade: facilitar criação de novos adapters sem modificar o core
- Flexibilidade: suportar múltiplas fontes de IA, boards e sistemas de comunicação
- Desacoplamento: configurações independentes de fornecedor específico
- Compatibilidade: não quebrar esteiras existentes na migração

## Métricas de sucesso
- Nenhuma esteira existente quebrada após migração
- Tempo para criar novo adapter reduzido de dias para horas
- Configurações centralizadas em pipe.yml
- Extinção do diretório .kiro/ com migração completa para .pipe/

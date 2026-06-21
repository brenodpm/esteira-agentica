# Épicos — Mudança de Arquitetura

Status: draft
Owner: product
Last updated: 2026-06-21

## Inputs
- Vision e Problem Space da mudança de arquitetura
- Análise da estrutura atual do projeto

## Épico: Definição da Arquitetura Hexagonal

**Objetivo:** Definir ports, adapters e estrutura de camadas para migração
**Escopo:** 
- Mapeamento de componentes atuais para a nova arquitetura
- Definição de interfaces (ports) para cada tipo de integração
- Especificação de adapters existentes e futuros
- Documentação detalhada da nova estrutura

**Fora de escopo:** 
- Implementação dos adapters
- Migração do código existente

## Épico: Reestruturação do Core

**Objetivo:** Implementar o domínio central isolado e interfaces definidas
**Escopo:**
- Refatoração do core business para ficar agnóstico a integrações
- Implementação dos ports definidos no épico anterior  
- Criação da camada de aplicação que orquestra o domínio
- Testes unitários para o core isolado

**Fora de escopo:**
- Migração dos adapters existentes
- Configurações de produção

## Épico: Migração de Adapters Existentes

**Objetivo:** Converter componentes atuais em adapters da nova arquitetura
**Escopo:**
- Migração do adapter GitHub Projects V2
- Migração do adapter de sistema de arquivos local
- Migração do adapter de agentes IA
- Validação de funcionamento idêntico ao atual

**Fora de escopo:**
- Novos adapters além dos existentes
- Otimizações de performance

## Épico: Unificação de Configurações

**Objetivo:** Centralizar todas as configurações no pipe.yml
**Escopo:**
- Migração de configurações de .kiro/ para .pipe/
- Extensão do pipe.yml para suportar configurações de adapters
- Remoção do diretório .kiro/
- Documentação da nova estrutura de configuração

**Fora de escopo:**
- Configurações de novos adapters não existentes
- Ferramentas de migração automática para usuários

## Épico: Preparação para Extensibilidade

**Objetivo:** Documentar e validar facilidade de criação de novos adapters
**Escopo:**
- Documentação detalhada para desenvolvimento de adapters
- Exemplo de adapter simples para referência
- Testes de integração da arquitetura completa
- Guia de migração para desenvolvedores

**Fora de escopo:**
- Implementação de novos adapters específicos
- Ferramentas visuais de configuração

# Épicos — Daily Report

Status: draft
Owner: product
Last updated: 2025-06-16

## Inputs
- `.pipe/boards/epic/analise-negocio/56-daily_report.md`

## Épico: Configuração de Relatórios

**Objetivo:** Permitir configurar quando e como os relatórios devem ser gerados
**Escopo:** 
- Configuração no pipe.yml para habilitar/desabilitar relatórios
- Definição de horário para geração automática
- Configuração de formato e destino do relatório
**Fora de escopo:** Envio por email ou mensagens (funcionalidade futura)

## Épico: Sistema de Diário Compartilhado

**Objetivo:** Criar mecanismo para agentes registrarem suas atividades
**Escopo:**
- Estrutura de diário comum para todos os agentes
- Padronização do formato de registros de atividade
- Persistência das informações de execução
**Fora de escopo:** Interface gráfica para visualização do diário

## Épico: Geração de Relatórios

**Objetivo:** Produzir relatórios consolidados das atividades diárias
**Escopo:**
- Coleta de informações dos diários dos agentes
- Geração de relatório estruturado com features executadas, bloqueadas e criadas
- Identificação de problemas e dependências em aberto
- Sugestão de próximas execuções
- Salvamento no diretório journal
**Fora de escopo:** Análise preditiva ou recomendações avançadas

## Épico: Agente de Relatório

**Objetivo:** Criar agente especializado na geração de relatórios diários
**Escopo:**
- Agente genérico que executa em horário configurado
- Lógica de consolidação das informações dos diários
- Formatação e estruturação do relatório final
**Fora de escopo:** Agentes especializados para diferentes tipos de relatório

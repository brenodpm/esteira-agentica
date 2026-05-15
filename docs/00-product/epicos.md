Status: approved
Owner: product-agent
Last updated: 2026-05-14T21:51:00-03:00

## Inputs
- statup.md
- docs/00-product/vision.md
- docs/00-product/problem-space.md

---

## Épico: Orquestração Automática de Agentes

**Objetivo:** Eliminar o humano como orquestrador, automatizando o acionamento e sequenciamento dos agentes de IA conforme o fluxo definido.  
**Escopo:** Lógica de orquestração, passagem de contexto entre agentes, gates de aprovação humana, execução via Kiro CLI.  
**Fora de escopo:** Interface visual, integração com ferramentas externas pagas, múltiplos agentes de IA simultâneos.

---

## Épico: Gestão de Tarefas

**Objetivo:** Organizar features, bugs, milestones e stories em um sistema de gestão integrado à esteira.  
**Escopo:** Suporte a metodologias (Kanban, Scrum, etc.), criação e atualização automática de itens pelo sistema, leitura de backlog para acionar agentes.  
**Fora de escopo:** Ferramentas pagas, integração com e-mail ou chat (fase futura).

---

## Épico: Integração com Git

**Objetivo:** Automatizar operações de versionamento integradas ao fluxo da esteira.  
**Escopo:** Integração com GitHub (inicial), suporte a gitflow configurável, criação de branches, commits e PRs automatizados.  
**Fora de escopo:** GitLab, Bitbucket e outros provedores (fase futura).

---

## Épico: Coleta de Métricas

**Objetivo:** Tornar o custo em tokens visível e controlável, além de auditar qualidade e velocidade do processo.  
**Escopo:** **[PRIORIDADE 1]** Custo em tokens por agente e por feature; tempo de execução por etapa; taxa de retrabalho; registro de delírios de IA.  
**Fora de escopo:** Dashboards visuais, integração com ferramentas de observabilidade externas.

## Changes
- Objetivo do épico de métricas reescrito para destacar custo em tokens como prioridade 1
- Motivo: alinhamento com prioridade definida pelo usuário

---

## Épico: Operação Remota

**Objetivo:** Permitir que o sistema rode de forma autônoma em qualquer máquina sem interação direta do usuário.  
**Escopo:** Todo contato com o humano via board/gestão de tarefas, aprovações remotas, configuração inicial local.  
**Fora de escopo:** Integração via e-mail e chat (fase futura), ferramentas pagas.

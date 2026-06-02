Status: approved
Owner: product-agent
Last updated: 2026-06-02

## Issue
#15 — Criar um manual do usuário para o projeto

## Inputs
- docs/00-product/vision.md
- docs/00-product/migration-plan.md
- docs/02-architecture/overview.md

---

## Contexto

A esteira agêntica é um sistema de orquestração de agentes de IA integrado ao GitHub e ao git. O projeto é público, com código e documentação em `brenodpm/esteira-agentica`. Para rodar, o usuário precisa de: dependências instaladas, arquivos de configuração (`esteira.yml`) e agentes Kiro (`.kiro/agents/`).

Hoje não existe um manual que guie esse processo de fora para dentro — partindo de um usuário que nunca viu o projeto.

---

## Problemas

- **[CRÍTICO]** Não existe instrução de como obter e instalar a esteira sem clonar o repositório inteiro
- Não existe ponto de entrada único que explique pré-requisitos, configuração e execução em sequência
- O `migration-plan.md` pressupõe que o usuário já tem o repositório clonado — não resolve o caso de adoção externa
- A ausência de um manual impede que o Épico de Adoção e Migração seja completado: sem documentação pública acessível, terceiros não conseguem adotar a esteira

---

## Impacto

- O projeto público fica inutilizável para adotantes externos
- Contradiz o objetivo declarado do Épico de Adoção e Migração
- O débito `debito-product-documentacao-publica-readme.md` permanece aberto mesmo após resolução formal

---

## Oportunidade

Criar um manual do usuário como artefato de produto — `docs/manual-usuario.md` — que cubra o caminho completo: download dos artefatos necessários, instalação de dependências, configuração mínima e execução. O README deve apontar para esse manual como porta de entrada.

A estrutura já está definida no `migration-plan.md`; o manual a formaliza como documento voltado ao usuário final, com linguagem direta e passo a passo executável.

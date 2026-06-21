# Problem Space — Mudança de Arquitetura

Status: draft
Owner: product
Last updated: 2026-06-21

## Inputs
- Issue epic/131-mudanca_de_arquitetura.md
- Análise do código fonte atual em src/
- Estrutura de configuração em .kiro/ e pipe.yml

## Contexto
O projeto "Esteira Agêntica" atualmente funciona como sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local. A arquitetura atual possui:

- Componentes monolíticos em src/ (github.py, agent.py, issues.py, sync.py)
- Configurações divididas entre .kiro/ e pipe.yml
- Integração fixa com GitHub Projects V2
- Suporte apenas a um provedor de IA (configurado via .kiro/)
- Ausência de abstrações para extensibilidade

## Problemas
- **Rigidez arquitetural**: Adicionar novos tipos de boards ou provedores de IA requer modificar código core
- **Acoplamento de configurações**: Configurações espalhadas entre .kiro/ e pipe.yml criam dependência de fornecedor específico
- **Limitação de integrações**: Impossível adicionar email, mensagens instantâneas ou outros sistemas sem reestruturação major
- **Barreira para contribuições**: Desenvolvedores externos não conseguem criar adapters facilmente
- **Manutenibilidade**: Mudanças em integrações afetam o core do sistema

## Impacto
- Desenvolvimento lento de novas funcionalidades
- Dificuldade para adoção por diferentes equipes com ferramentas variadas
- Risco de vendor lock-in com provedores específicos
- Barreira para crescimento da comunidade open source
- Retrabalho frequente para pequenas mudanças de integração

## Oportunidade
Com a arquitetura hexagonal, o projeto pode:
- Tornar-se agnóstico a ferramentas específicas
- Acelerar criação de novos adapters pela comunidade
- Suportar múltiplos provedores simultaneamente
- Facilitar testes e manutenção através do isolamento
- Posicionar-se como padrão para esteiras agênticas extensíveis

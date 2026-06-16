# Critérios de Aceitação Refinados — Guia de Desenvolvimento e Extensão

Status: approved
Owner: requirements
Last updated: 2026-06-16

## CA-001: Criar Agente Personalizado

**Dado** que sigo o guia de criação de agentes personalizados

**Quando** implemento um novo agente conforme os passos documentados

**Então** consigo:
- Definir o propósito e as responsabilidades do agente
- Registrar callbacks e handlers necessários
- Integrar o agente ao sistema de orquestração
- Testar o agente localmente antes de integrar
- Validar que o agente funciona sem erros

**Evidência de teste:**
- [ ] Documentação contém seção "Como Criar um Agente"
- [ ] Inclui template de código reutilizável
- [ ] Template pode ser copiado e adaptado com edições mínimas
- [ ] Exemplo pronto funciona end-to-end (criar, registrar, rodar)

## CA-002: Contribuir com o Projeto

**Dado** que desejo contribuir com o projeto (bug, melhoria ou feature)

**Quando** leio o guia de contribuição

**Então** compreendo:
- Como reportar e documentar um issue
- Qual é o processo de branch e PR
- Quais são os padrões de código esperados
- Como rodar testes localmente
- Qual é o padrão de commit e PR description

**Evidência de teste:**
- [ ] Documentação contém seção "Guia de Contribuição"
- [ ] Explica fluxo: fork → branch → PR → merge
- [ ] Inclui checklist de antes de PR (testes, lint, docs)
- [ ] Referencia padrões (branch naming, commit message)

## CA-003: Entender a Arquitetura

**Dado** que desejo estender o sistema

**Quando** leio a documentação de arquitetura

**Então** consigo:
- Identificar componentes principais do sistema
- Entender o fluxo de dados entre componentes
- Compreender como agentes se integram
- Identificar pontos de extensão

**Evidência de teste:**
- [ ] Documentação contém diagrama ou descrição de arquitetura alto nível
- [ ] Descreve componentes: orchestrator, agents, board sync, GitHub integration
- [ ] Explica como dados fluem: GitHub → Board → Agents → Actions
- [ ] Identifica pelo menos 3 pontos de extensão (ex: novo tipo de agente, novo modelo, novo webhook)

## CA-004: Debug de Problemas

**Dado** que encontro um problema ao executar a esteira

**Quando** consulto a documentação técnica

**Então** encontro:
- Como ativar logs detalhados
- Onde estão armazenados os logs
- Como interpretar mensagens de erro
- Exemplos de troubleshooting comum

**Evidência de teste:**
- [ ] Documentação inclui seção "Debugging e Logs"
- [ ] Explica variáveis de ambiente para logs
- [ ] Mostra exemplos de erro comum e solução
- [ ] Referencia arquivo de logs e estrutura de dados

## CA-005: Exemplos de Agentes Adicionais

**Dado** que quero criar um tipo de agente específico

**Quando** consulto a lista de agentes sugeridos

**Então** encontro inspiração e padrões para agentes como:
- Code Reviewer
- Empacotador (bundler/packager)
- Analista de Infra DevOps
- Especialista em AWS
- Especialista em Azure

**Evidência de teste:**
- [ ] Documentação lista agentes sugeridos
- [ ] Cada agente tem descrição de responsabilidade
- [ ] Incluir pelo menos um exemplo de implementação (mesmo que simplificado)
- [ ] Mostrar como registrar novo agente na esteira

# Arquitetura em Alto Nível

Este documento descreve a arquitetura da Esteira Agêntica, explicando seus componentes principais e fluxo de dados para desenvolvedores que desejam entender como estender o sistema.

## Visão Geral

A Esteira Agêntica é um sistema de automação que sincroniza bidirecionalmente entre GitHub Projects V2 e sistema de arquivos local, executando agentes especializados para processar issues automaticamente.

```
GitHub Projects ←→ Board Sync ←→ Local Files ←→ Orchestrator ←→ Agents
                                                      ↓
                                                   Actions
```

## Componentes Principais

### Orchestrator

**Localização:** `src/__main__.py`
**Responsabilidade:** Motor principal que coordena todo o ciclo de execução

- Executa loop contínuo de sincronização e processamento
- Gerencia throttling e rate limiting
- Coordena interação entre todos os outros componentes
- Implementa cleanup de logs e gestão de snapshots

**Quando é usado:** Continuamente como processo principal da esteira

### Agents

**Localização:** `src/agent.py` e `.kiro/agents/`
**Responsabilidade:** Executores especializados que processam issues conforme sua área de atuação

- Carrega configurações específicas de cada agente
- Gera prompts contextualizados para cada tarefa
- Resolve branches e fluxos git conforme configuração
- Executa ações específicas do domínio (arquitetura, desenvolvimento, testes, etc.)

**Quando é usado:** Quando uma issue entra numa coluna que tem agente configurado

### Board Sync

**Localização:** `src/sync.py` e `src/issues.py`
**Responsabilidade:** Sincronização bidirecional entre GitHub Projects V2 e sistema local

- Mantém estrutura de boards e colunas sincronizada
- Propaga movimentação de issues entre colunas
- Gerencia snapshots para detectar mudanças
- Remove estruturas obsoletas localmente

**Quando é usado:** No início de cada ciclo e quando detecta mudanças estruturais

### GitHub Integration

**Localização:** `src/github.py`
**Responsabilidade:** Interface com APIs do GitHub via GraphQL

- Executa operações no GitHub Projects V2
- Gerencia rate limiting e throttling de mutations
- Resolve metadados de projetos e boards
- Trata erros de comunicação com GitHub

**Quando é usado:** Sempre que há necessidade de ler ou escrever dados no GitHub

## Fluxo de Dados

### GitHub → Board

1. **Detecção**: Board Sync detecta mudanças no GitHub Projects
2. **Download**: GitHub Integration busca dados atualizados via GraphQL
3. **Persistência**: Board Sync salva issues como arquivos locais em `.pipe/boards/`

### Board → Agents

1. **Seleção**: Orchestrator identifica tarefas elegíveis via `pick_task`
2. **Contexto**: Agent carrega configuração e constrói prompt específico
3. **Execução**: Agent processa a tarefa conforme sua especialização

### Agents → Actions

1. **Processamento**: Agent executa lógica de negócio da tarefa
2. **Artefatos**: Cria ou modifica arquivos conforme necessário
3. **Movimentação**: Move issue para próxima coluna indicando conclusão

### Actions → GitHub

1. **Sync Local**: Board Sync detecta mudanças nos arquivos locais
2. **Upload**: GitHub Integration propaga mudanças para GitHub Projects
3. **Persistência**: GitHub Projects reflete novo status das issues

## Pontos de Extensão

### 1. Novos Tipos de Agent

**Como:** Criar arquivo em `.kiro/agents/novo-agent.json` com configuração específica
**Quando:** Para adicionar nova especialização (ex: agente de segurança, performance)
**Exemplo:** Agent de documentação que gera docs automaticamente

### 2. Novos Boards e Workflows

**Como:** Adicionar nova configuração em `pipe.yml` na seção `boards`
**Quando:** Para novos tipos de processo (ex: board de releases, board de suporte)
**Exemplo:** Board específico para code reviews com fluxo customizado

### 3. Integrações Externas

**Como:** Estender `src/github.py` ou criar novos módulos de integração
**Quando:** Para conectar com outras ferramentas (Jira, Slack, CI/CD)
**Exemplo:** Notificações automáticas no Slack quando issues mudam de status

### 4. Actions Customizadas

**Como:** Estender lógica de processamento em agents existentes ou criar novos
**Quando:** Para implementar ações específicas do domínio
**Exemplo:** Geração automática de releases notes baseada em issues concluídas

### 5. Filtros e Seletores de Task

**Como:** Modificar `src/pick_task.py` para implementar nova lógica de seleção
**Quando:** Para priorização customizada ou critérios específicos de execução
**Exemplo:** Priorizar tasks por impacto de negócio ou complexidade técnica

## Considerações de Arquitetura

- **Single Loop**: Orchestrator executa em loop único para evitar concorrência
- **Estado Local**: `.pipe/` mantém estado sincronizado com GitHub
- **Rate Limiting**: GitHub Integration implementa throttling para evitar limits
- **Extensibilidade**: Configuração via `pipe.yml` permite extensões sem código
- **Rastreabilidade**: Logs estruturados permitem debugging e auditoria

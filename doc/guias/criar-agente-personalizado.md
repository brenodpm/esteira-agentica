# Como Criar um Agente Personalizado

Este guia mostra como criar e integrar um novo agente à Esteira Agêntica.

## Visão Geral

Um agente é um executor especializado que processa issues conforme sua área de atuação. Cada agente tem:
- **Responsabilidades específicas** (ex: arquitetura, desenvolvimento, testes)  
- **Configuração JSON** em `.kiro/agents/`
- **Integração automática** ao orchestrator via `pipe.yml`

## Template de Agente

```json
{
  "name": "meu-agente",
  "description": "Agente que faz X quando Y acontece",
  "model": "claude-sonnet-4",
  "prompt": "Você é um especialista em X.\n\n## Papel\n\nFaça Y quando receber Z.\n\n## O que você faz\n\n- Lista de responsabilidades\n- Máximo 5 itens\n\n## O que você NÃO faz\n\n- Lista de limites\n- Máximo 5 itens\n\n## Execução\n\n1. Passo 1\n2. Passo 2\n3. Passo 3\n\n## Artefatos que você produz\n\n- Tipo de saída esperada",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob", "code"]
}
```

**Como este prompt aparece formatado:**

```
Você é um especialista em X.

## Papel

Faça Y quando receber Z.

## O que você faz

- Lista de responsabilidades
- Máximo 5 itens

## O que você NÃO faz

- Lista de limites
- Máximo 5 itens

## Execução

1. Passo 1
2. Passo 2
3. Passo 3

## Artefatos que você produz

- Tipo de saída esperada
```

## Como Criar um Agente

### 1. Definir Responsabilidades

Defina claramente:
- **Domínio**: qual área o agente atua (ex: segurança, performance)  
- **Entrada**: que tipo de issue processa
- **Saída**: que artefatos produz
- **Limites**: o que não faz

### 2. Criar Arquivo de Configuração

Crie `.kiro/agents/meu-agente.json`:

```json
{
  "name": "security",
  "description": "Agente de segurança — analisa código para vulnerabilidades",
  "model": "claude-sonnet-4",
  "prompt": "Você é um especialista em segurança de software.\n\n## Papel\n\nAnalisar código para identificar vulnerabilidades de segurança.\n\n## O que você faz\n\n- Executa análise estática de segurança\n- Identifica padrões inseguros no código\n- Sugere correções específicas\n- Documenta vulnerabilidades encontradas\n\n## O que você NÃO faz\n\n- Não corrige código automaticamente\n- Não implementa novas funcionalidades\n- Não altera arquitetura\n\n## Execução\n\n1. Ler código da issue\n2. Executar análise de segurança\n3. Documentar findings\n4. Mover para próxima coluna\n\n## Artefatos que você produz\n\n- Relatório de segurança em `doc/security/`\n- Lista de vulnerabilidades com severidade",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob", "code"]
}
```

### 3. Registrar no Pipeline  

Edite `pipe.yml` para registrar o agente em uma coluna:

```yaml
boards:
  task:
    columns:
      analise-seguranca:
        name: "Análise de Segurança"
        agent: security          # nome do arquivo .json
        gitevents: []
        change:
          advance: code-review
```

### 4. Integrar ao Orchestrator

O sistema detecta automaticamente:
- Novo arquivo em `.kiro/agents/` é carregado
- Coluna com `agent: security` executa o agente  
- Issues que entram na coluna são processadas

### 5. Testar Localmente

Teste antes de integrar:

```bash
# Teste o agente diretamente
kiro-cli chat --agent security --no-interactive < test-input.txt

# Ou teste com uma issue real
echo "Issue de teste com código para análise" | kiro-cli chat --agent security --no-interactive
```

**Critério de sucesso:**
- Agente executa sem erro
- Produz saída esperada
- Não quebra quando input está vazio

## Exemplo Prático Completo

Este exemplo cria um agente de documentação que gera README para repositórios.

**1. Arquivo:** `.kiro/agents/docs.json`
```json
{
  "name": "docs",
  "description": "Gerador de documentação automática",
  "model": "claude-haiku-4.5",
  "prompt": "Você gera documentação clara e concisa.\n\n## Papel\n\nGerar README.md para repositórios baseado no código existente.\n\n## O que você faz\n\n- Analisa estrutura do projeto\n- Gera README com instalação e uso\n- Inclui exemplos básicos\n\n## O que você NÃO faz\n\n- Não documenta APIs complexas\n- Não gera docs técnicos detalhados\n\n## Execução\n\n1. Ler estrutura do projeto\n2. Identificar linguagem e ferramentas  \n3. Gerar README.md na raiz\n\n## Artefatos que você produz\n\n- README.md na raiz do projeto",
  "tools": ["fs_read", "fs_write", "glob", "code"]
}
```

**Como este prompt aparece formatado:**
```
Você gera documentação clara e concisa.

## Papel

Gerar README.md para repositórios baseado no código existente.

## O que você faz

- Analisa estrutura do projeto
- Gera README com instalação e uso
- Inclui exemplos básicos

## O que você NÃO faz

- Não documenta APIs complexas
- Não gera docs técnicos detalhados

## Execução

1. Ler estrutura do projeto
2. Identificar linguagem e ferramentas  
3. Gerar README.md na raiz

## Artefatos que você produz

- README.md na raiz do projeto
```

**2. Configuração em `pipe.yml`:**
```yaml
boards:
  task:
    columns:
      documentacao:
        name: "Documentação"
        agent: docs
        change:
          advance: done
```

**3. Teste:**
```bash
# Criar input de teste
echo "Gere README para este projeto Python com FastAPI" > test-docs.txt

# Executar agente
kiro-cli chat --agent docs --no-interactive < test-docs.txt

# Verificar saída
ls -la README.md
```

## Pontos de Extensão

Esta implementação usa os pontos de extensão documentados em [arquitetura](../architecture-overview.md):

- **Novos Tipos de Agent**: Arquivo `.kiro/agents/<nome>.json`
- **Integração ao Orchestrator**: Configuração `agent:` em colunas do `pipe.yml`  
- **Actions Customizadas**: Prompt e tools específicos do domínio

## Referências

- [Arquitetura em Alto Nível](../architecture-overview.md) — pontos de extensão
- [Guia de Contribuição](guia-contribuicao.md) — padrões de código

# Agentes e Níveis de Esforço

Agentes são responsáveis por executar ações em colunas específicas. O sistema de esforço controla qual modelo de IA é usado e a profundidade de análise.

## Mapeamento Global de Effort

Na raiz do `pipe.yml`, você pode opcionalmente definir seus próprios níveis de esforço. Esta configuração é totalmente customizável — você decide quais níveis existem, como são nomeados e quais modelos usam:

```yaml
effort:
  low:
    model: claude-haiku-4.5    # Modelo rápido e econômico
    effort: low                # Profundidade de análise
  medium:
    model: claude-sonnet-4     # Modelo balanceado
    effort: medium
  high:
    model: claude-sonnet-4     # Modelo avançado
    effort: high               # Análise profunda, raciocínio detalhado
```

> **Nota**: Esta configuração é um exemplo. Você pode criar quantos níveis quiser, nomeá-los como preferir e escolher os modelos conforme sua disponibilidade e necessidade.

### Modelos Disponíveis

Os modelos disponíveis dependem do seu acesso às APIs de IA (chaves, quotas, região). Você escolhe quais usar conforme sua disponibilidade:

- **claude-haiku-4.5**: Rápido, economiza tokens, bom para tarefas simples
- **claude-sonnet-4**: Balanceado, recomendado para a maioria dos casos  
- **claude-opus-4**: Mais poderoso, ideal para análise complexa

> **Importante**: A esteira não fornece ou limita os modelos. Você precisa configurar credenciais e acesso para cada modelo que quiser usar.

### Níveis de Effort (Exemplo)

Esta é uma configuração de referência — você pode criar níveis diferentes conforme sua necessidade:

- **low**: Respostas diretas, sem raciocínio estendido. Use para tarefas repetitivas.
- **medium**: Raciocínio padrão, análise básica. Padrão da maioria das colunas.
- **high**: Raciocínio profundo, análise minuciosa. Use para decisões complexas.

## Atribuindo Agentes a Colunas

Cada coluna que requer automação deve indicar qual agente executará. O campo `effort` é opcional — se omitido, usa o padrão do agente:

```yaml
columns:
  requisitos:
    name: "Requisitos"
    agent: requirements        # Agente responsável  
    effort: high              # [OPCIONAL] Esforço específico da coluna
    acao: "..."
  
  simples:
    name: "Processamento Simples"
    agent: custom-processor    # Sem effort definido — usa padrão do agente
    acao: "..."
```

### Agentes de Exemplo

Você cria e controla todos os agentes em `.kiro/agents/`. Os exemplos abaixo são sugestões de especialização — você pode criar quantos agentes quiser, com os nomes e responsabilidades que fizerem sentido para seu projeto:

- **product**: Análise de negócio, documentação de requisitos
- **requirements**: Especificação funcional, critérios de aceitação  
- **architecture**: Design técnico, decisões arquiteturais
- **engineering**: Implementação de código
- **quality**: Testes, validação
- **tech-lead**: Planejamento técnico, decomposição de tarefas
- **devops**: Deploy, infraestrutura
- **optimizer**: Análise de performance e otimizações

> **Importante**: Esta é apenas uma lista de referência. Você define quais agentes existem criando arquivos `.kiro/agents/<nome>.json` conforme sua necessidade.

## Resolução de Precedência

A esteira usa esta ordem para determinar modelo e esforço:

1. **Padrão do agente** (arquivo `.kiro/agents/<nome>.json`) — fallback quando nada é especificado
2. **Configuração da coluna** em `pipe.yml` (`effort: high`) — sobrescreve padrão do agente  
3. **Tag na issue** (`/effort high`) — se `allow-overwrite: true` na coluna

### Exemplo de Resolução

Issue tem `/effort low`, coluna tem `effort: high`:
- Se `allow-overwrite: true` → usa `low` (tag sobrescreve)
- Se `allow-overwrite: false` → usa `high` (coluna prevalece)
- Se coluna não tem effort definido → usa padrão do agente

## Configuração Completa

Exemplo mostrando flexibilidade — você pode usar níveis customizados e omitir effort onde não precisar:

```yaml
effort:
  # Níveis customizados para este projeto
  rapido:
    model: claude-haiku-4.5
    effort: low
  normal:  
    model: claude-sonnet-4
    effort: medium
  critico:
    model: claude-opus-4  
    effort: high

boards:
  story:
    name: "User Stories"
    todo: backlog
    columns:
      requisitos:
        name: "Requisitos"
        agent: business-analyst     # Agente customizado
        effort: critico            # Sempre usa nível "critico"
        allow-overwrite: false     # Issue não pode sobrescrever
        acao: "Levantar requisitos funcionais e não-funcionais"
        change:
          advance: arquitetura

      arquitetura:
        name: "Arquitetura" 
        agent: tech-designer
        effort: critico
        allow-overwrite: false
        acao: "Definir design técnico"
        change:
          advance: desenvolvimento

      desenvolvimento:
        name: "Desenvolvimento"
        agent: engineering
        # effort omitido — usa padrão do agente "engineering"
        allow-overwrite: true      # Issue pode pedir nível específico
        acao: "Implementar conforme arquitetura"
        change:
          advance: concluido
```

## Boas Práticas

1. **Use níveis simples** para tarefas repetitivas, reformatação, integração simples
2. **Use níveis médios** para desenvolvimento padrão, revisões básicas  
3. **Use níveis avançados** para decisões arquiteturais, análise complexa, troubleshooting
4. **Seja conservador com níveis avançados** — usa mais tokens e tempo
5. **Defina `allow-overwrite: true`** apenas onde faz sentido permitir override
6. **Documente o padrão de cada agente** em `.kiro/agents/` se customizar comportamento
7. **Omita `effort` em colunas** onde o padrão do agente é suficiente

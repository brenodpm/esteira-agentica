# Agentes e Níveis de Esforço

Agentes são responsáveis por executar ações em colunas específicas. O sistema de esforço controla qual modelo de IA é usado e a profundidade de análise.

## Mapeamento Global de Effort

Na raiz do `pipe.yml`, defina os níveis de esforço:

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

### Modelos Disponíveis

- **claude-haiku-4.5**: Rápido, economiza tokens, bom para tarefas simples
- **claude-sonnet-4**: Balanceado, recomendado para a maioria dos casos
- **claude-opus-4**: Mais poderoso, ideal para análise complexa

### Níveis de Effort

- **low**: Respostas diretas, sem raciocínio estendido. Use para tarefas repetitivas.
- **medium**: Raciocínio padrão, análise básica. Padrão da maioria das colunas.
- **high**: Raciocínio profundo, análise minuciosa. Use para decisões complexas.

## Atribuindo Agentes a Colunas

Cada coluna que requer automação deve indicar qual agente executará:

```yaml
columns:
  requisitos:
    name: "Requisitos"
    agent: requirements        # Agente responsável
    effort: high              # Esforço específico da coluna
    acao: "..."
```

### Agentes Disponíveis

- **product**: Análise de negócio, documentação de requisitos
- **requirements**: Especificação funcional, critérios de aceitação
- **architecture**: Design técnico, decisões arquiteturais
- **engineering**: Implementação de código
- **quality**: Testes, validação
- **tech-lead**: Planejamento técnico, decomposição de tarefas
- **devops**: Deploy, infraestrutura
- **optimizer**: Análise de performance e otimizações

## Resolução de Precedência

A esteira usa esta ordem para determinar modelo e esforço:

1. **Padrão do agente** (arquivo `.kiro/agents/<nome>.json`)
2. **Configuração da coluna** em `pipe.yml` (`effort: high`)
3. **Tag na issue** (`/effort high`) — se `allow-overwrite: true` na coluna

### Exemplo de Resolução

Issue tem `/effort low`, coluna tem `effort: high`:
- Se `allow-overwrite: true` → usa `low` (tag sobrescreve)
- Se `allow-overwrite: false` → usa `high` (coluna prevalece)

## Configuração Completa

```yaml
effort:
  low:
    model: claude-haiku-4.5
    effort: low
  medium:
    model: claude-sonnet-4
    effort: medium
  high:
    model: claude-sonnet-4
    effort: high

boards:
  story:
    name: "User Stories"
    todo: backlog
    columns:
      requisitos:
        name: "Requisitos"
        agent: requirements
        effort: high           # Esta coluna sempre usa high effort
        allow-overwrite: false # Issue não pode sobrescrever
        acao: "Levantar requisitos funcionais e não-funcionais"
        change:
          advance: arquitetura

      arquitetura:
        name: "Arquitetura"
        agent: architecture
        effort: high
        allow-overwrite: false
        acao: "Definir design técnico"
        change:
          advance: desenvolvimento

      desenvolvimento:
        name: "Desenvolvimento"
        agent: engineering
        effort: medium         # Tarefas rotineiras usam medium
        allow-overwrite: true  # Mas issue pode pedir mais análise
        acao: "Implementar conforme arquitetura"
        change:
          advance: concluido
```

## Boas Práticas

1. **Use `low` effort** para tarefas repetitivas, reformatação, integração simples
2. **Use `medium` effort** para desenvolvimento padrão, revisões básicas
3. **Use `high` effort** para decisões arquiteturais, análise complexa, troubleshooting
4. **Seja conservador com `high` effort** — usa mais tokens e tempo
5. **Defina `allow-overwrite: true`** apenas onde faz sentido permitir override
6. **Documente o padrão de cada agente** em `.kiro/agents/` se customizar comportamento

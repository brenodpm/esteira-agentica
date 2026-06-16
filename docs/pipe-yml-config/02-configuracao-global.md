# Configuração Global

A seção `pipe` define comportamentos globais da esteira.

## Campo: pipe.agent.timeout

Define o tempo máximo (em segundos) que uma operação individual pode levar antes de ser cancelada.

```yaml
pipe:
  agent:
    timeout: 1200  # 20 minutos
```

**Impacto**: Operações que excedem este tempo são interrompidas. Use valores maiores para tarefas complexas que requerem análise profunda.

## Campo: pipe.agent.sleeptime

Define o intervalo (em segundos) entre cada ciclo do loop principal da esteira.

```yaml
pipe:
  agent:
    sleeptime: 1800  # 30 minutos
```

**Impacto**: Quanto menor, mais frequente a esteira verifica novas tarefas. Valores menores consomem mais recursos e APIs.

## Campo: ttl-log

Tempo de vida (em dias) dos arquivos de log antes de serem removidos automaticamente.

```yaml
ttl-log: 10  # Remove logs com mais de 10 dias
```

**Impacto**: Controla limpeza automática de histórico de logs.

## Campo: doc

Caminho do diretório onde a documentação do projeto será armazenada pelos agentes.

```yaml
doc: docs/
```

**Impacto**: Agentes que precisam gerar documentação (como `product` e `requirements`) salvam seus artefatos aqui.

## Exemplo Completo

```yaml
pipe:
  agent:
    timeout: 1200
    sleeptime: 1800

ttl-log: 10
doc: docs/
```

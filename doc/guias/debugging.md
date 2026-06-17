# Debugging e Logs

Este guia explica como ativar logs detalhados, onde estão armazenados, estrutura dos dados e como interpretar mensagens de erro comuns na Esteira Agêntica.

## Como ativar logs detalhados (variáveis de ambiente)

O sistema de logs é configurado através do arquivo `pipe.yml` e usa as seguintes configurações:

### Configuração de TTL dos Logs
- **`ttl-log`**: Tempo em dias para manter arquivos de log (padrão: 10 dias)
  - Exemplo no `pipe.yml`: `ttl-log: 10`
  - Logs mais antigos são automaticamente removidos

### Nível de Log
O sistema usa logging Python padrão com nível INFO por padrão. Para logs mais detalhados:

- **DEBUG**: Para ativar logs de debug, modifique o nível em `src/log.py`:
  ```python
  logger.setLevel(logging.DEBUG)
  ```

- **Timeout do Agente**: Configurado em `pipe.yml`:
  ```yaml
  pipe:
    agent:
      timeout: 1200      # timeout em segundos
      sleeptime: 1800    # intervalo entre execuções
  ```

## Onde estão armazenados os logs

### Estrutura de Diretórios
```
logs/
├── yyyy-MM-dd.log              # Logs diários principais
├── yyyy-MM-dd-a.log            # Logs extras do mesmo dia
├── yyyy-MM-dd-b.log            # Logs extras do mesmo dia
└── <issue_id>/                 # Logs específicos de issues
    └── yyyyMMddHHmmss-<board>-<col>-<agent>.log
```

### Exemplos de Localização
- **Log principal**: `logs/2026-06-17.log`
- **Log de issue específica**: `logs/111/20260617123000-task-desenvolvimento-implementacao.log`
- **Logs de agente**: Organizados por ID da issue em subdiretórios

## Estrutura de dados dos logs

### Formato Padrão
```
HH:MM:SS LEVEL MENSAGEM
```

### Exemplo de Log Real
```
09:21:28 INFO Sync iniciado...
09:21:28 INFO [sync_github] alter-remote-boards=true — sincronizando boards remotos
09:21:33 INFO [push_boards] Concluído
09:21:35 INFO [task] l-sync #79 → code-review
09:21:46 INFO [epic] b-new #114 Horario de funcionamento criado localmente
```

### Campos dos Logs
- **Timestamp**: Formato HH:MM:SS
- **Level**: INFO, WARNING, ERROR, DEBUG
- **Contexto**: Entre colchetes `[componente]` quando aplicável
- **Mensagem**: Descrição da operação ou evento
- **IDs**: Issues referenciadas com `#<numero>`
- **Operações**: Códigos como `l-sync`, `b-new`, `auto-advance`

## Exemplos de erro comum e solução

### Erro 1: Rate Limit GitHub
**Mensagem de erro:**
```
WARNING Rate limit — push de boards adiado
```
**Causa provável:** API do GitHub atingiu limite de requisições
**Solução:** O sistema aguarda automaticamente. Verifique configuração de token GitHub se persistir.

### Erro 2: Board não resolvido
**Mensagem de erro:**
```
WARNING Cache: board 'task' não resolvido: <error>
```
**Causa provável:** Configuração incorreta do board no `pipe.yml` ou problemas de conectividade
**Solução:** 
1. Verificar sintaxe do `pipe.yml`
2. Confirmar existência do board no GitHub
3. Validar permissões do token

### Erro 3: Arquivo de issue removido
**Mensagem de erro:**
```
DEBUG [task] #123 detectado l-del (arquivo removido)
```
**Causa provável:** Issue foi deletada localmente ou por sincronização
**Solução:** Normal - sistema detectou remoção e sincronizará com GitHub

### Erro 4: Timeout de agente
**Mensagem de erro:**
```
ERROR Agent timeout após 1200 segundos
```
**Causa provável:** Tarefa complexa excedeu tempo limite configurado
**Solução:**
1. Aumentar `timeout` em `pipe.yml`
2. Verificar se tarefa não está travada
3. Revisar logs específicos do agente em `logs/<issue_id>/`

## Como interpretar mensagens de erro

### Níveis de Severidade
- **INFO**: Operações normais do sistema (sync, movimentação de issues)
- **WARNING**: Situações que podem causar atraso mas não impedem funcionamento
- **ERROR**: Falhas que impedem execução de operações específicas
- **DEBUG**: Informações detalhadas para troubleshooting (apenas quando ativado)

### Códigos de Operação
- **`l-sync`**: Sincronização local → GitHub (movimentação de issue)
- **`l-del`**: Remoção local detectada
- **`b-new`**: Criação de nova issue/board
- **`auto-advance`**: Movimentação automática entre colunas
- **`[sync_github]`**: Operações de sincronização com GitHub
- **`[push_boards]`**: Sincronização de boards

### Contexto de Rastreamento
1. **ID da Issue**: Sempre referenciada como `#<numero>`
2. **Board e Coluna**: Indicados na movimentação `coluna_origem → coluna_destino`
3. **Timestamp**: Permite correlacionar eventos em sequência
4. **Componente**: Entre colchetes indica módulo responsável pela operação

### Exemplo de Análise
```log
09:21:35 INFO [task] l-sync #79 → code-review
```
- **09:21:35**: Horário da operação
- **INFO**: Operação normal
- **[task]**: Board de tasks
- **l-sync**: Sincronização local → remoto
- **#79**: ID da issue
- **→ code-review**: Movida para coluna code-review

Para troubleshooting avançado, consulte logs específicos da issue em `logs/<issue_id>/` que contêm detalhes da execução do agente.

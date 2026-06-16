# Esteira Agêntica

Sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local.

## Como rodar

```bash
python -m src
```

## pipe.yml — Documentação Completa

Arquivo de configuração central da esteira. Toda a estrutura de boards, colunas e fluxos é definida aqui. O pipe.yml é **mandatório** — qualquer alteração nele sobrescreve a estrutura local e remota.

### Guia Rápido

Para começar rapidamente, confira:
- [📖 Visão Geral](docs/pipe-yml-config/01-visao-geral.md) — Estrutura geral do pipe.yml
- [⚙️ Configuração Global](docs/pipe-yml-config/02-configuracao-global.md) — Timeout, sleeptime, doc path
- [🌿 Git Flows](docs/pipe-yml-config/03-gitflows.md) — Como setup branches (feature, epic, hotfix, etc)
- [📊 Boards e Colunas](docs/pipe-yml-config/04-boards-e-colunas.md) — Criar e organizar workflows
- [🤖 Agentes e Esforço](docs/pipe-yml-config/05-agentes-e-esforco.md) — Atribuir agentes e controlar profundidade de análise
- [💡 Exemplos Práticos](docs/pipe-yml-config/06-exemplos-praticos.md) — Casos de uso: novo board, customizar effort, gitflow, validação humana, etc

### Referência Rápida

#### Seção `pipe`
Configurações globais do agente.

```yaml
pipe:
  agent:
    timeout: 1200    # Segundos antes de cancelar operação
    sleeptime: 1800  # Intervalo entre ciclos (segundos)
```

#### Seção `effort`
Mapeamento de níveis para modelos e profundidade.

```yaml
effort:
  low:
    model: claude-haiku-4.5
    effort: low      # Rápido, respostas diretas
  medium:
    model: claude-sonnet-4
    effort: medium   # Padrão para a maioria
  high:
    model: claude-sonnet-4
    effort: high     # Raciocínio profundo, análise detalhada
```

#### Seção `git`
Setup de repositório e gitflows.

```yaml
git:
  repo: "owner/repo"
  flow:
    base: main
    cleanup: true    # Remove branches locais após cada operação
    
    feature:
      prefix: feature
      description: "Branch de feature"
      create: main    # De onde cria
      merge: main     # Para onde vai o PR
```

#### Seção `boards`
Define todos os boards do projeto.

```yaml
boards:
  story:
    name: "User Stories"
    todo: backlog           # Coluna inicial
    priority: 3             # Ordem de processamento (0 = mais alta)
    flow: epic              # Gitflow usado
    columns:
      backlog:
        name: Backlog
        agent: requirements # Se ausente = manual (humano)
        effort: medium      # Sobrescreve esforço do agente
        acao: "Entender demanda e criar documentação"
        change:
          advance: arquitetura  # Próxima coluna
      arquitetura:
        name: "Arquitetura"
        agent: architecture
        effort: high
        acao: "Definir design técnico"
        change:
          advance: desenvolvimento
```

### Resolução de Precedência (Effort)

1. Padrão do agente em `.kiro/agents/<nome>.json`
2. Configuração da coluna em `pipe.yml`
3. Tag `/effort` na issue (se `allow-overwrite: true`)

### Estrutura Local

```
.pipe/
  boards/
    <board-id>/
      <col-id>/
        (issues como arquivos)
```

**Regra de prioridade**:
1. `pipe.yml` — fonte da verdade
2. Disco local — reflete o pipe.yml
3. GitHub — recebe atualizações

## Estrutura local

```
.pipe/
  snapshot.json   # estado do último sync (mtime + boards)
  boards/
    <board-id>/
      <col-id>/
        (issues serão arquivos aqui)
```

### Regra de prioridade

A sincronização segue esta ordem de precedência:

1. **pipe.yml** — é a fonte da verdade para estrutura de boards/colunas
2. **Disco local** — reflete o pipe.yml; movimentação de arquivos (issues) dentro das colunas será propagada para o GitHub
3. **GitHub** — recebe as atualizações; nunca sobrescreve o pipe.yml ou a estrutura local

## Pendências: ações local → GitHub (TODO)

As seguintes ações ainda **não estão implementadas** mas são necessárias:

| Ação | Trigger | Efeito no GitHub |
|------|---------|------------------|
| Criar issue | Arquivo novo em coluna (status `l-new`) | Criar issue no repo + adicionar ao project board |
| Mover issue | Arquivo movido de coluna (status `l-sync`) | Mover card para nova coluna no project |
| Deletar issue | Arquivo removido (status `l-del`) | Fechar issue no GitHub |
| Postar comentário | Arquivo `*-write.md` com conteúdo | Postar body como comentário na issue e limpar o arquivo |

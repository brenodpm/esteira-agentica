# Esteira Agêntica

Sincronizador bidirecional entre GitHub Projects V2 e sistema de arquivos local.

## Como rodar

```bash
python -m src
```

## pipe.yml

Arquivo de configuração central da esteira. Toda a estrutura de boards, colunas e fluxos é definida aqui. O pipe.yml é **mandatório** — qualquer alteração nele sobrescreve a estrutura local e remota.

### pipe

Configurações globais do agente.

| Campo             | Descrição                                                        |
|-------------------|------------------------------------------------------------------|
| `pipe.agent.timeout`   | Tempo máximo (em segundos) que uma operação individual pode levar antes de ser cancelada. |
| `pipe.agent.sleeptime` | Intervalo (em segundos) entre cada ciclo do loop principal.       |

### effort

Mapeamento global de níveis de effort para model e profundidade de raciocínio. Usado quando a issue sobrescreve o effort via tag `/effort`.

| Campo             | Descrição                                                        |
|-------------------|------------------------------------------------------------------|
| `effort.<level>.model`  | Modelo a ser usado quando o nível for aplicado.             |
| `effort.<level>.effort` | Profundidade de raciocínio (`low`, `medium`, `high`).       |

Resolução de model/effort (ordem de precedência):
1. `.kiro/agents/<name>.json` — valores padrão do agente
2. `pipe.yml` coluna `effort` — sobrescreve o effort do agente
3. Tag `/effort` na issue — sobrescreve model e effort usando o mapa `effort.<level>` (requer `allow-overwrite: true` na coluna)

### doc

Caminho do diretório onde a documentação do projeto será armazenada pelos agentes.

### git

Configurações de integração com o repositório GitHub.

| Campo         | Descrição                                                                 |
|---------------|---------------------------------------------------------------------------|
| `git.repo`    | Identificador do repositório no formato `owner/repo`.                     |
| `git.flow.base`    | Branch base do projeto (normalmente `main`).                         |
| `git.flow.cleanup` | Se `true`, após cada operação de branch, retorna para a base e remove branches locais usadas. |

#### Tipos de flow

Cada tipo de flow define como branches são criadas e mergeadas. São usados nos boards para indicar qual gitflow seguir.

| Campo       | Descrição                                                                 |
|-------------|---------------------------------------------------------------------------|
| `prefix`    | Prefixo das branches criadas (ex: `feature/`, `fix/`).                    |
| `description` | Descrição legível do propósito desse tipo de flow.                      |
| `create`    | Branch de origem — de onde a nova branch será criada. Pode ser uma branch fixa (`main`) ou um prefixo de outro flow (ex: `release`), que será resolvido via issue. |
| `merge`     | Branch de destino — para onde o merge/PR será direcionado. Mesma lógica de resolução. |

### boards

Define os boards do projeto. Cada board corresponde a um GitHub Project V2 e um diretório local em `boards/<board-id>/`.

| Campo      | Descrição                                                                 |
|------------|---------------------------------------------------------------------------|
| `bugs`     | ID do board onde bugs são criados.                                         |
| `needs`    | ID do board onde demandas para humanos ou outros agentes são criadas.      |
| `name`     | Nome visível do board no GitHub Projects.                                  |
| `todo`     | ID da coluna inicial onde issues novas entram.                             |
| `priority` | Prioridade de execução do board (0 = mais alta). Boards com menor valor são processados primeiro. |
| `flow`     | Tipo de gitflow associado a esse board (referencia um dos flows definidos em `git.flow`). |
| `parallel` | Se `false`, issues desse board são processadas uma por vez (padrão: paralelo). |

#### columns

Cada board possui um mapa de colunas. Cada coluna vira um subdiretório em `.pipe/boards/<board-id>/<col-id>/`.

| Campo          | Descrição                                                              |
|----------------|------------------------------------------------------------------------|
| `name`         | Nome visível da coluna no GitHub Projects (campo Status).               |
| `desc`         | Descrição do que acontece nessa etapa.                                  |
| `agent`        | Nome do agente responsável por executar a ação nessa coluna. Se ausente, a coluna é manual (humano). |
| `effort`       | Nível de raciocínio do agente: `low`, `medium` ou `high`. Opcional, padrão `medium`. Níveis mais altos gastam mais tokens em análise profunda e geração minuciosa; níveis mais baixos produzem respostas mais rápidas e diretas. |
| `gitevents`    | Lista opcional de eventos git da coluna: `create` (cria branch conforme gitflow), `keep` (padrão — branch já existe e é mantida), `merge` (solicita merge request ao concluir). Aceita combinação de eventos. |
| `acao`         | Instrução textual do que o agente deve fazer quando uma issue chega nessa coluna. |
| `git_commit`   | Se `true`, o agente faz commit das alterações produzidas.               |
| `git_merge`    | Se `true`, a coluna envolve criação de PR ou merge para a branch destino do flow. |
| `wait_children`| Se `true`, a issue fica parada até que todas as issues filhas estejam concluídas. |
| `allow-overwrite` | Se `true`, permite que a tag `/effort` na issue sobrescreva model e effort da coluna. Padrão: `false`. |

#### change

Define as transições possíveis a partir de uma coluna.

| Campo      | Descrição                                                                |
|------------|--------------------------------------------------------------------------|
| `advance`  | ID da próxima coluna quando a etapa é concluída com sucesso.              |
| `reprovar` | ID da coluna para onde a issue volta em caso de reprovação humana.        |
| `cancelar` | ID da coluna de cancelamento.                                             |
| `falha`    | ID da coluna para onde a issue volta quando testes falham.                |
| `bloquear` | ID da coluna de bloqueio (dependência externa).                           |

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

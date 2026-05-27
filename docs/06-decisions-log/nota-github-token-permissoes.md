Status: draft
Owner: engineering-agent
Last updated: 2026-05-27

## Nota: Permissões do GitHub Access Token

> Conteúdo destinado ao README do projeto.

### Fine-grained personal access token (recomendado)

**Repository permissions** (repositório `brenodpm/esteira-agentica`):

| Permissão     | Nível                  |
|---------------|------------------------|
| Issues        | Read and write         |
| Pull requests | Read and write         |
| Contents      | Read and write         |
| Metadata      | Read-only (automático) |

**Account permissions**:

| Permissão | Nível          |
|-----------|----------------|
| Projects  | Read and write |

### Classic token (alternativa mais simples)

Scopes necessários:
- `repo` — cobre issues, PRs, contents, labels, milestones
- `project` — cobre GitHub Projects (board)

> ⚠️ O classic token com `repo` dá acesso a **todos** os repositórios da conta. Prefira o fine-grained para maior segurança.

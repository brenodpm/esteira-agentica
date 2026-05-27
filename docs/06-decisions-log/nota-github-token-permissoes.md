Status: resolved
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

---

## ⚠️ CT-090 — Token sem escopo `project`

**Sintoma:** `gh project list --owner brenodpm` retorna:
```
GraphQL: Resource not accessible by personal access token (user.projectsV2.nodes.0)
```

**Causa:** O token PAT configurado não possui o escopo `project` (classic) ou a permissão `Projects: Read and write` (fine-grained).

**Solução — recriar o token:**

### Fine-grained token
1. Acessar https://github.com/settings/personal-access-tokens/new
2. Em **Repository permissions**, configurar:
   - Issues: Read and write
   - Pull requests: Read and write
   - Contents: Read and write
3. Em **Account permissions**, configurar:
   - **Projects: Read and write** ← obrigatório para o board
4. Gerar o token e reautenticar: `gh auth login`

### Classic token
1. Acessar https://github.com/settings/tokens/new
2. Selecionar os scopes:
   - `repo` — issues, PRs, contents, labels, milestones
   - **`project`** ← obrigatório para GitHub Projects (board)
3. Gerar o token e reautenticar: `gh auth login`

**Verificação após recriar:**
```bash
gh auth status
gh project list --owner brenodpm
```

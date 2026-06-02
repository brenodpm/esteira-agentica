# Gitflow

Status: approved
Owner: requirements-agent
Last updated: 2026-05-14T22:14:00-03:00

## Fluxo padrão

```
main
 └── develop
      ├── feature/<nome>   → nova funcionalidade
      ├── fix/<nome>       → correção de bug
      └── release/<versão> → preparação de release
main
 └── hotfix/<nome>         → correção urgente em produção
```

## Regras

- Nenhum commit direto em `main` ou `develop`
- Todo merge via Pull Request com aprovação humana obrigatória
- `feature/*` e `fix/*` partem de `develop` e retornam para `develop`
- `release/*` parte de `develop`, merge em `main` e back-merge em `develop`
- `hotfix/*` parte de `main`, merge em `main` e back-merge em `develop`

## Configurabilidade

O gitflow é configurável por projeto. O padrão acima é aplicado quando nenhuma configuração específica for definida.

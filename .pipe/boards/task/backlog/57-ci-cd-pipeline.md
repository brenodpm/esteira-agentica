# Configurar CI/CD pipeline para validação e geração automática

effort: medium

## User Story
49-pagina_inicial_de_documentacao

## Descrição
Criar workflow GitHub Actions que executa Index Generator automaticamente em cada push para `main`, valida links, e atualiza `/docs/index.html` no repositório.

## Escopo técnico
- Criar `.github/workflows/docs-build.yml`
- Trigger: push em `main` ou `docs/` alterado
- Executar Index Generator
- Validar HTML (W3C)
- Validar todos links via curl/httpie (CI/CD)
- Verificar acessibilidade com axe CLI
- Commit automático de `/docs/index.html` se geração OK
- Falhar build se validações falharem
- Cache de dependências (Python)

## Fora de escopo
- Deploy em GitHub Pages (assumir Pages já configurado)
- Notificações via Slack/email
- Revert automático de commits

## Critério de aceite
- Workflow criado e ativado
- Executa Index Generator em cada push
- Valida HTML gerado
- Valida links (mock para externas)
- Falha se acessibilidade inválida
- Commit automático se tudo OK
- Sem secrets vazados em logs

/blocked_by 56-index-generator
/branch epic/49-pagina_inicial_de_documentacao

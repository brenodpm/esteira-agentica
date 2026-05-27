Status: approved
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/00-product/vision.md
- docs/00-product/problem-space.md
- docs/01-requirements/meeting-01.md

## Restrições técnicas

- Apenas ferramentas gratuitas (sem APIs pagas de terceiros além do modelo de IA já em uso)
- Integração inicial exclusivamente com GitHub (GitLab, Bitbucket fora de escopo)
- Execução em máquina local única — sem infraestrutura distribuída
- Toda interação com o usuário deve ocorrer via GitHub (issues, comentários, labels) — sem UI própria
- Kiro CLI como runtime de execução dos agentes
- Gitflow configurável por projeto; padrão: `main`, `develop`, `release/*`, `hotfix/*`, `feature/*`, `fix/*`
- Board configurável por projeto; padrão: Backlog / In Progress / Done (GitHub Projects)

## Premissas

- O usuário possui conta GitHub com acesso ao repositório alvo
- `gh` CLI autenticado na máquina de execução
- `git` disponível e configurado localmente
- Kiro CLI disponível e autenticado
- Um único projeto/repositório por instância de execução (multi-repo é fase futura)
- Agentes executam sequencialmente (sem paralelismo entre agentes na mesma feature)
- O modelo de IA subjacente expõe contagem de tokens por chamada

## Requisitos não funcionais

| Atributo | Requisito |
|---|---|
| Custo em tokens | Minimizar tokens por execução; cada agente lê apenas o contexto necessário; saídas enxutas |
| Rastreabilidade | Toda execução deve ser auditável via artefatos versionados em git e registros no GitHub |
| Confiabilidade | Falha em um agente não deve corromper estado; orquestrador deve retomar do último gate aprovado |
| Configurabilidade | Gitflow e board configuráveis por projeto sem alteração de código |
| Operabilidade | Sistema deve operar sem presença física do usuário após configuração inicial |
| Segurança | Credenciais (tokens GitHub, chaves) nunca persistidas em artefatos versionados |
| Manutenibilidade | Módulos com responsabilidades isoladas; sem acoplamento cruzado entre agents e integrations |

Status: accepted
Owner: architecture-agent
Last updated: 2026-05-28

## Inputs
- docs/02-architecture/overview.md
- docs/02-architecture/constraints.md
- docs/agents/context.md
- docs/agents/*.md
- docs/00-product/migration-plan.md

## Contexto

A esteira define 6 agentes especializados (product, requirements, architecture, tech-lead, engineering, quality). Até agora, esses agentes existiam apenas como documentação em `docs/agents/*.md` — sem definição formal de runtime. O Kiro CLI suporta agentes customizados via `.kiro/agents/*.json`, que permitem definir prompt, ferramentas permitidas, atalhos de teclado e injeção de contexto automática.

A questão é: onde vive a definição executável dos agentes da esteira?

## Decisão

Os agentes da esteira são definidos como **Kiro agents** em `.kiro/agents/<role>.json`. Cada arquivo JSON é a definição executável do agente correspondente, contendo:

- `prompt`: comportamento, regras, artefatos produzidos e paths de output
- `allowedTools`: ferramentas que o agente pode usar (fs_read, fs_write, grep, glob, execute_bash, code)
- `contextFiles`: arquivos injetados automaticamente no início de cada sessão (context.md, agent doc, artifact-map.md)
- `hooks.agentSpawn`: script que injeta estado da esteira (feature atual, etapa, status)

A documentação em `docs/agents/*.md` permanece como referência humana e fonte de verdade conceitual. O `.kiro/agents/*.json` é a implementação executável.

## Justificativa

- **Kiro CLI já é o runtime definido** (ver constraints.md e adr-001): usar o mecanismo nativo de agentes elimina a necessidade de um runner customizado para acionar agentes
- **Injeção de contexto automática** via `contextFiles` garante que cada agente recebe o contrato de artefatos e as regras do projeto sem depender de prompt manual
- **`allowedTools` como contrato de segurança**: cada agente só acessa as ferramentas que seu papel exige — product não executa bash, engineering pode
- **Portabilidade**: copiar `.kiro/agents/` para qualquer projeto é suficiente para ter a esteira funcionando — sem dependências adicionais além do Kiro CLI
- **Rastreabilidade**: a definição dos agentes fica versionada em git junto com o restante do projeto

## Consequências

Positivas:
- Agentes prontos para uso imediato via `kiro-cli chat --agent <role>`
- Contexto da esteira injetado automaticamente em cada sessão
- Portabilidade total: `.kiro/agents/` é o único artefato necessário para replicar a esteira
- Sem código de orquestração adicional para acionar agentes manualmente

Negativas:
- Duplicação parcial entre `docs/agents/*.md` (referência conceitual) e `.kiro/agents/*.json` (definição executável) — mudanças precisam ser refletidas em ambos
- Dependência do Kiro CLI como runtime — não funciona com outros clientes de IA sem adaptação

Riscos:
- Divergência entre `docs/agents/*.md` e `.kiro/agents/*.json` se evoluírem de forma independente → mitigação: `docs/agents/*.md` é a fonte de verdade conceitual; `.kiro/agents/*.json` é derivado e deve ser atualizado junto

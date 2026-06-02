Status: accepted
Owner: architecture-agent
Last updated: 2026-05-26

## Inputs
- docs/02-architecture/adr-004-mecanismo-bloqueio-tasks.md

## Contexto

Agentes frequentemente precisam de informações que só o humano pode fornecer (requisitos ambíguos, decisões de negócio, validações). Esse fluxo precisa ser assíncrono — o agente não pode bloquear execução aguardando resposta em tempo real.

## Decisão

Perguntas ao humano são modeladas como issues bloqueantes com label `needs-human`:

1. O agente cria uma issue com as perguntas e label `needs-human`
2. Adiciona label `blocked` na issue corrente referenciando a issue de perguntas
3. O orquestrador pula a issue bloqueada e processa outras tasks disponíveis
4. O humano responde via **comentário na issue** de perguntas e fecha a issue (ou adiciona label `answered`)
5. O orquestrador detecta a resolução, injeta as respostas no contexto do agente e recoloca a issue original no backlog
6. O agente retoma com o contexto atualizado — pode gerar novas perguntas (nova issue `needs-human`) ou atuar efetivamente na task

**Fora de escopo (versão futura):** notificação e resposta via e-mail, Teams, Discord ou outras ferramentas de mensageria.

## Justificativa

- Reutiliza o mesmo mecanismo de bloqueio do ADR-004 sem estrutura adicional
- GitHub Issues é a interface já estabelecida para toda interação humana com o sistema
- O ciclo pergunta → resposta → retomada é naturalmente assíncrono e auditável
- Múltiplas rodadas de perguntas são suportadas sem alteração arquitetural

## Consequências

- Positivas: interação humana totalmente rastreável e auditável; sem canal adicional na v1; humano pode responder de qualquer lugar via GitHub
- Negativas: latência dependente da disponibilidade do humano (aceitável — é assíncrono por design)
- Riscos: humano não responde — orquestrador mantém a issue bloqueada indefinidamente; mitigado por SLA configurável com escalada futura

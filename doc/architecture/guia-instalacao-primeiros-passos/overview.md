# Architecture Overview — Guia de Instalação e Primeiros Passos

Status: draft
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Issue #52: Guia de Instalação e Primeiros Passos (story arquitetura)
- docs/requirements/guia-instalacao-primeiros-passos/business-rules.md
- docs/requirements/guia-instalacao-primeiros-passos/non-functional-requirements.md
- pipe.yml: configurações globais do projeto
- README.md: documentação existente
- src/__main__.py: ponto de entrada do projeto

## Visão geral

Sistema de documentação estático que fornece guia de instalação unificado para a esteira agêntica. O guia deve habilitar usuários novos a instalar, configurar e executar sua primeira automação em menos de 15 minutos, incluindo conceptualização dos componentes essenciais.

## Estilo arquitetural

**Documentação como Código** — guia implementado como arquivo markdown único e versionado junto ao código.

**Justificativa:** 
- Simplicidade para manutenção e descoberta
- Consistência com pipeline existente (git flow)
- Facilita validação via automação futura
- Permite evolução incremental via PR review

## Componentes

| Componente | Responsabilidade |
|-----------|------------------|
| Guia Principal | Documento markdown unificado com instalação, conceitos e hello-world |
| Seção Conceitos | Explicação prévia de agentes, boards, pipe.yml e model/effort |
| Procedimento Instalação | Instruções step-by-step para ambiente local e Docker |
| Hello-World | Exemplo funcional de primeira automação |
| Troubleshooting | Mapear 5 erros comuns e soluções |
| Validação Scripts | Scripts básicos para verificar instalação (opcional) |

## Fluxo principal

```
1. Usuário acessa guia único → docs/guides/installation-guide.md
2. Lê conceitos fundamentais (agentes, boards, pipe.yml, effort)
3. Verifica pré-requisitos (Python 3.8+, Git, Docker opcional)
4. Executa instalação (clone → deps → execução básica)
5. Segue hello-world (criar issue → mover board → observar automação)
6. Em caso de erro → consulta troubleshooting integrado
```

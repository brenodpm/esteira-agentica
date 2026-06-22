# ADR-001 — Documento único vs múltiplos arquivos

Status: accepted
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Regra de negócio RN-007: Um único arquivo de documentação
- Comparação com documentações existentes (README.md)

## Contexto

Precisamos decidir se o guia de instalação será um documento markdown único ou múltiplos arquivos organizados por tópico (instalação, conceitos, troubleshooting, etc.).

## Decisão

Implementar como documento markdown único em `docs/guides/installation-guide.md`.

## Justificativa

- **Simplicidade de descoberta:** usuário encontra tudo em um lugar
- **Manutenção centralizada:** evita dessincronia entre arquivos relacionados
- **Experiência linear:** fluxo natural de leitura conceitos → instalação → hello-world
- **Atende RN-007:** requisito explícito de arquivo único
- **Facilita versionamento:** mudanças aparecem em diff único

## Consequências

- **Positivas:**
  - Descoberta mais fácil para usuários novos
  - Menos overhead de navegação entre arquivos
  - Facilita copy-paste sequencial
  
- **Negativas:**
  - Arquivo pode ficar extenso com o tempo
  - Manutenção de seções específicas requer edição do arquivo inteiro
  
- **Riscos:**
  - Se arquivo crescer muito, pode prejudicar carregamento em viewers web
  - Conflitos de merge mais prováveis com múltiplos editores

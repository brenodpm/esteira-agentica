# Constraints — Guia de Instalação e Primeiros Passos

Status: draft
Owner: architecture
Last updated: 2026-06-22

## Inputs
- Issue #52: Guia de Instalação e Primeiros Passos (story arquitetura)
- docs/requirements/guia-instalacao-primeiros-passos/non-functional-requirements.md
- pipe.yml: configurações do projeto

## Restrições técnicas

- **Arquivo único:** Toda documentação deve estar em um markdown único para facilitar descoberta
- **Markdown padrão:** Usar apenas sintaxe markdown compatível com GitHub/GitLab viewers
- **Sem dependências externas:** Guia deve funcionar offline após clone inicial
- **Versionamento junto ao código:** Documento vive no repositório principal, não wiki separada
- **Copy-paste ready:** Blocos de código devem ser executáveis sem edição manual

## Premissas

- Usuários têm conhecimento básico de terminal e Git
- Ambiente de desenvolvimento já possui Python 3.8+ instalado
- Acesso à internet durante instalação inicial (para download de dependências)
- GitHub CLI disponível para operações de branch/PR (opcional para hello-world)
- Docker disponível para setup alternativo (mas não obrigatório)

## Requisitos não-funcionais

| Atributo | Requisito |
|----------|----------|
| **Tempo de absorção** | Conceitos devem ser compreendidos em < 10 minutos |
| **Tempo de instalação** | Setup completo em < 15 minutos (exclui downloads) |
| **Tempo de execução** | Hello-world deve completar em < 30 segundos |
| **Compatibilidade** | Python 3.8+, Linux/macOS/Windows |
| **Segurança** | Zero secrets ou credenciais reais em exemplos |
| **Usabilidade** | Blocos de código prontos para copy-paste |
| **Disponibilidade** | Funcional offline após clone |
| **Manutenibilidade** | Estrutura extensível para casos avançados futuros |

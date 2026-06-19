# Requisitos Não-Funcionais — Guia de Instalação e Primeiros Passos

Status: approved
Owner: requirements
Last updated: 2026-06-19

## Inputs
- Issue #52: Guia de Instalação e Primeiros Passos (story requisitos)
- pipe.yml: configurações do projeto
- src/__main__.py: ponto de entrada
- Regras de Negócio deste épico

## Performance

- **Tempo de install inicial**: Máximo 5 minutos para instalar todas as dependências (exclui download inicial)
- **Tempo de execução hello-world**: Primeiro run deve completar em menos de 30 segundos
- **Tempo de leitura**: Desenvolvedor deve absorver conceitos em menos de 10 minutos

## Segurança

- **Sem segredos em exemplo**: Hello-world não deve incluir tokens reais, senhas ou credenciais
- **Documentação de variáveis de ambiente**: Guia deve explicar onde armazenar `.env` e quais vars são necessárias
- **Sem modificações estruturais perigosas**: Exemplos nunca devem instruir modificação de pipe.yml diretamente

## Escalabilidade

- **Documentação agnóstica de versão de Python**: Suportar Python 3.8+
- **Independência de plataforma**: Instruções funcionam em Linux, macOS, Windows
- **Estrutura extensível**: Exemplo hello-world deve ser facilmente expandível para casos mais complexos

## Disponibilidade

- **Documentação offline-first**: Guia deve funcionar sem acesso à internet após clone
- **Sem dependências externas em hello-world**: Exemplo não requer API calls, webhooks ou serviços third-party
- **Sem rate limiting**: Exemplo não deve disparar rate limits do GitHub durante execução

## Usabilidade

- **Linguagem clara**: Texto sem jargão técnico ou com jargão explicado quando necessário
- **Copy-paste ready**: Blocos de código devem ser copiáveis direto sem edição
- **Screenshots/diagrama visual**: Quando possível, incluir representação visual de conceitos como boards
- **Feedback imediato**: Desenvolvedor deve ter confirmação clara de sucesso a cada passo

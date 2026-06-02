Status: approved
Owner: product-agent
Last updated: 2026-06-02

## Issue
#15 — Criar um manual do usuário para o projeto

## Inputs
- docs/00-product/vision.md
- docs/00-product/migration-plan.md
- docs/00-product/epicos.md
- docs/02-architecture/overview.md
- esteira.yml

---

## Problema

O projeto está público no GitHub, mas um usuário externo que encontra o repositório não consegue colocar a esteira para rodar sem entender a estrutura interna. Não existe um ponto de entrada claro que explique o que é necessário instalar, como configurar e como executar — sem precisar clonar o projeto ou ter conhecimento prévio.

## Solução

Criar um manual do usuário autocontido que guie qualquer pessoa do zero até a esteira rodando. O manual cobre: o que é necessário instalar, como obter os arquivos da esteira (sem clonar o repo), como configurar o `esteira.yml` e os agentes, e como executar o orquestrador.

O canal de distribuição do manual é o próprio README do repositório ou um arquivo `docs/manual-usuario.md` linkado a partir dele.

## Público-alvo

Desenvolvedor ou tech lead que quer adotar a esteira em seu próprio projeto, sem contexto prévio sobre este repositório, sem acesso à máquina onde o projeto foi desenvolvido.

## Proposta de valor

Reduz a barreira de entrada de "preciso entender o projeto todo" para "sigo o manual e estou rodando em menos de 30 minutos".

## Resultado esperado

- Usuário instala dependências seguindo o manual
- Usuário obtém os arquivos da esteira (download/release) sem clonar
- Usuário configura `esteira.yml` e `.kiro/agents/` para seu projeto
- Usuário executa `python -m src` e a esteira inicia

## Restrições

- O manual não deve exigir clone do repositório da esteira — apenas os arquivos necessários para rodar
- Deve funcionar em Linux e macOS
- Deve ser possível seguir sem suporte humano (autoexplicativo)

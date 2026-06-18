# Guia de Contribuição

Este guia explica como contribuir para o projeto Esteira Agêntica, incluindo o núcleo da esteira e suas integrações externas.

## Escopo de Contribuição

O projeto está dividido em duas áreas principais:

- **Núcleo da esteira**: Sistema de sincronização, agentes, processamento de issues e fluxo de trabalho
- **Integrações externas**: Conectores com GitHub Projects, sistemas externos e extensões

Ambas as áreas seguem os mesmos padrões de contribuição descritos neste guia.

## Como Reportar Issues

Para reportar um problema ou sugerir uma melhoria:

### Campos Obrigatórios

- **Título**: Descrição clara e concisa do problema
- **Descrição**: Contexto detalhado do que está acontecendo
- **Passos para reproduzir**: Lista numerada de como reproduzir o problema
- **Resultado esperado**: O que deveria acontecer
- **Resultado atual**: O que está acontecendo

### Exemplo de Issue Bem Formado

```
Título: Sincronização falha com GitHub Projects quando board tem mais de 100 issues

Descrição:
A sincronização com GitHub Projects falha quando o board contém mais de 100 issues, 
retornando erro de timeout.

Passos para reproduzir:
1. Configurar board com 150+ issues
2. Executar `python -m src`
3. Aguardar processo de sincronização

Resultado esperado:
Todas as issues devem ser sincronizadas sem erros

Resultado atual:
Processo falha com timeout após ~2 minutos
```

## Fluxo de Contribuição

### 1. Fork
- Faça fork do repositório para sua conta GitHub
- Clone seu fork localmente: `git clone https://github.com/SEU_USER/esteira-agentica.git`

### 2. Branch
- Crie uma branch para sua contribuição: `git checkout -b feature/minha-contribuicao`
- Use o padrão de naming definido na seção "Padrões de Código"

### 3. Pull Request
- Faça push da sua branch: `git push origin feature/minha-contribuicao`
- Abra Pull Request no GitHub apontando para a branch `main`
- Preencha template de PR com descrição detalhada

### 4. Merge
- Aguarde revisão do código
- Implemente mudanças solicitadas se necessário
- Após aprovação, o merge será realizado pela equipe

## Padrões de Código

### Branch Naming
Use o formato: `tipo/issue-numero-descricao`

Exemplos:
- `feature/123-sincronizacao-github`
- `fix/456-erro-timeout-boards`
- `docs/789-guia-contribuicao`

### Commit Message
Use o formato: `Tipo: Descrição clara`

Exemplos:
- `feat: adiciona sincronização bidirecional com GitHub Projects`
- `fix: corrige timeout em boards com muitas issues`
- `docs: atualiza guia de instalação`

### Lint
- Projeto usa configuração padrão de Python (definida em `pyproject.toml`)
- Execute `ruff check` antes de fazer commit
- Configure seu editor para aplicar formatação automática

### Testes
- Cobertura mínima de 80% para código novo
- Testes unitários em `tests/unit/`
- Testes de integração em `tests/integration/`
- Use pytest como framework de testes

### Documentação
- Docstrings obrigatórias para funções públicas
- Comments para lógica complexa
- Atualize documentação relevante em `doc/`

## Como Rodar Testes

### Todos os Testes
```bash
pytest
```

### Testes Específicos
```bash
# Por arquivo
pytest tests/unit/test_sync.py

# Por função
pytest tests/unit/test_sync.py::test_sync_boards

# Por padrão
pytest -k "sync"
```

### Ferramenta/Framework
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Configuração**: `pyproject.toml`

## Checklist de Antes de PR

Antes de criar seu Pull Request, verifique:

- [ ] **Testes passando**: `pytest` executa sem erros
- [ ] **Lint sem erros**: `ruff check` não reporta problemas
- [ ] **Documentação atualizada**: Arquivos em `doc/` refletem suas mudanças
- [ ] **Cobertura de testes**: Código novo tem testes correspondentes
- [ ] **Commit messages**: Seguem o padrão estabelecido
- [ ] **Branch naming**: Segue convenção `tipo/numero-descricao`
- [ ] **Funcionalidade testada**: Testou manualmente sua implementação

## Referências

- [Padrões de Branch Naming](https://conventional-commits.org/)
- [Padrões de Commit Message](https://www.conventionalcommits.org/)
- [Configuração de Desenvolvimento](../README.md#como-rodar)
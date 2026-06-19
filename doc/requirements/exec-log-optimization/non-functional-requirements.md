# Requisitos Não-Funcionais — Otimização via Exec Log

Status: approved
Owner: requirements
Last updated: 2026-06-19

## Inputs
- Issue #54: Base para otimização
- Business Rules (mesmo épico)

## Performance

- **Logging não deve impactar execução**: Escrita em `logs/exec.log` deve ser assíncrona ou buffered, com latência ≤ 10ms.
- **Otimizador lê log eficientemente**: Carregamento e parsing de `logs/exec.log` deve completar em ≤ 5s, independente do tamanho (até 100MB).
- **Otimizador processa análise rapidamente**: Identificação de padrões de ineficiência (tempo alto, custo alto, repetições) deve completar em ≤ 30s.

## Segurança

- **Log contém dados sensíveis**: `logs/exec.log` não é versionado em git (deve estar em `.gitignore`).
- **Acesso restrito**: Apenas o agente otimizador e sistema de monitoramento podem ler/escrever em `logs/exec.log`.
- **Sem exposição de prompts**: Tokens/prompts específicos não são registrados no log — apenas IDs de agentes e contagens.

## Escalabilidade

- **Log cresce indefinidamente**: Otimizador deve processar log de qualquer tamanho sem falhas de memória.
- **Deleção é obrigatória**: Após cada ciclo de otimização, `logs/exec.log` é deletado para evitar crescimento descontrolado.
- **Suporta múltiplos agentes em paralelo**: Escrita concorrente no log deve ser thread-safe (usa lock ou append-only).

## Disponibilidade

- **Falha de logging não bloqueia execução**: Se escrita em `logs/exec.log` falhar, agente continua executando sem erro crítico (pode logar warning).
- **Otimizador é tolerante a log ausente**: Se `logs/exec.log` não existir, otimizador não falha (mensagem informativa, nenhuma ação).

## Formato e Parsing

- **Formato é imutável**: Uma vez definido (RN-002), não muda para evitar quebra de retrocompatibilidade.
- **Campos são sempre presentes**: Nenhum campo opcional ou condicional. Parser pode fazer split direto por `;`.

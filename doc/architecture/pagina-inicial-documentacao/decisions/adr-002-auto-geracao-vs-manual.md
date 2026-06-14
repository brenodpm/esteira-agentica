# ADR-002 — Auto-geração vs Manutenção Manual

Status: accepted
Owner: architecture
Last updated: 2024-06-14

## Inputs
- Requisito de não duplicação de conteúdo
- Necessidade de manutenibilidade

## Contexto
A página inicial pode ser mantida manualmente ou gerada automaticamente baseada na estrutura de arquivos existente.

## Decisão
Implementar geração automática baseada em:
- Estrutura de diretórios em `/docs`
- Metadados nos arquivos Markdown (frontmatter)
- Mapeamento configurável de perfis para seções

## Justificativa
- Evita dessincronia entre estrutura real e página inicial
- Reduz overhead de manutenção manual
- Garante consistência ao longo do tempo

## Consequências
- Positivas: Sincronização automática, menor esforço de manutenção
- Negativas: Menor controle sobre layout específico
- Riscos: Dependência de convenções de metadados

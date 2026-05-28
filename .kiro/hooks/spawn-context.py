#!/usr/bin/env python3
"""
agentSpawn hook — injeta contexto da esteira no início de cada sessão de agente.

Lê state.json e config/project.json do projeto atual e imprime um bloco de
contexto estruturado que o Kiro injeta no início da conversa do agente.
"""
import json
import sys
from pathlib import Path


def main() -> None:
    cwd = Path.cwd()

    state_path = cwd / "state.json"
    config_path = cwd / "config" / "project.json"

    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    config = json.loads(config_path.read_text()) if config_path.exists() else {}

    repo = config.get("repo", "não configurado")
    sequence = config.get("agents_sequence", [])
    current_step = state.get("current_step")
    current_feature = state.get("current_feature")
    issue_number = state.get("issue_number")
    status = state.get("status", "idle")
    rework = state.get("rework", False)

    # Posição na sequência
    if current_step and sequence:
        try:
            pos = sequence.index(current_step) + 1
            step_info = f"{pos}/{len(sequence)}"
        except ValueError:
            step_info = "?"
    else:
        step_info = "início"

    lines = [
        "## Contexto da esteira",
        f"- Repositório: {repo}",
        f"- Status: {status}",
    ]

    if current_feature:
        lines.append(f"- Feature em andamento: {current_feature}")
    if issue_number:
        lines.append(f"- Issue: #{issue_number}")
    if current_step:
        lines.append(f"- Etapa atual: {current_step} ({step_info})")
    if rework:
        lines.append("- ⚠️ REWORK: artefato anterior foi rejeitado — revisar antes de produzir nova versão")
    if sequence:
        lines.append(f"- Sequência completa: {' → '.join(sequence)}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()

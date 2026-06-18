"""Testes para documentação de arquitetura em alto nível."""

import os
from pathlib import Path


def test_ct001_arquivo_documentacao_existe():
    """CT-001: Arquivo de documentação existe em local correto."""
    # Verificar existência de arquivo em doc/architecture-overview.md
    doc_path = Path("doc/architecture-overview.md")
    
    assert doc_path.exists(), f"Arquivo {doc_path} não encontrado"
    assert doc_path.suffix == ".md", "Arquivo deve ter extensão .md"


def test_ct002_contem_diagrama_ou_descricao():
    """CT-002: Diagrama ou descrição visual de arquitetura."""
    doc_path = Path("doc/architecture-overview.md")
    content = doc_path.read_text()
    
    # Verificar presença de palavras-chave que indicam arquitetura visual
    indicators = [
        "componentes", "fluxo", "diagrama", "arquitetura", 
        "orchestrator", "agents", "board sync", "GitHub integration"
    ]
    
    found_indicators = sum(1 for indicator in indicators if indicator.lower() in content.lower())
    assert found_indicators >= 4, "Documento deve conter descrição visual clara de arquitetura"


def test_ct003_descreve_componentes_principais():
    """CT-003: Descrição dos 4 componentes principais."""
    doc_path = Path("doc/architecture-overview.md")
    content = doc_path.read_text().lower()
    
    required_components = ["orchestrator", "agents", "board sync", "github integration"]
    
    for component in required_components:
        assert component.replace(" ", "") in content.replace(" ", ""), \
            f"Componente '{component}' não encontrado na documentação"


def test_ct004_documenta_fluxo_dados():
    """CT-004: Fluxo de dados documentado."""
    doc_path = Path("doc/architecture-overview.md")
    content = doc_path.read_text().lower()
    
    # Verificar sequência: GitHub → Board → Agents → Actions
    flow_elements = ["github", "board", "agents", "actions"]
    
    for element in flow_elements:
        assert element in content, f"Elemento '{element}' não encontrado no fluxo de dados"


def test_ct005_identifica_pontos_extensao():
    """CT-005: Pontos de extensão identificados."""
    doc_path = Path("doc/architecture-overview.md")
    content = doc_path.read_text().lower()
    
    # Procurar por indicadores de pontos de extensão
    extension_indicators = [
        "extensão", "extensibilidade", "customização", "personalização",
        "plugin", "hook", "callback", "ponto de extensão"
    ]
    
    found_indicators = sum(1 for indicator in extension_indicators if indicator in content)
    assert found_indicators >= 1, "Documento deve identificar pontos de extensão"

import os
import pytest

def test_guia_contribuicao_exists():
    """CT-006: Arquivo está em doc/guias/guia-contribuicao.md"""
    file_path = "doc/guias/guia-contribuicao.md"
    assert os.path.exists(file_path), f"Arquivo {file_path} não encontrado"
    
    # Verificar se é markdown válido (possui extensão .md)
    assert file_path.endswith(".md"), "Arquivo deve ser markdown"

def test_guia_contem_fluxo_completo():
    """CT-001: Fluxo fork → branch → PR → merge documentado"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificar se contém as 4 etapas
    assert "Fork" in content, "Deve conter seção sobre Fork"
    assert "Branch" in content, "Deve conter seção sobre Branch"
    assert "Pull Request" in content, "Deve conter seção sobre Pull Request"
    assert "Merge" in content, "Deve conter seção sobre Merge"

def test_guia_contem_checklist_pr():
    """CT-002: Checklist de antes de PR com testes, lint e docs"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Checklist" in content, "Deve conter checklist"
    assert "testes" in content.lower(), "Checklist deve mencionar testes"
    assert "lint" in content.lower(), "Checklist deve mencionar lint"
    assert "documentação" in content.lower(), "Checklist deve mencionar documentação"

def test_guia_contem_padroes_naming():
    """CT-003: Padrões de branch naming e commit message"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Branch Naming" in content, "Deve conter seção sobre branch naming"
    assert "Commit Message" in content, "Deve conter seção sobre commit message"
    assert "feature/" in content, "Deve conter exemplo de branch feature"

def test_guia_contem_reportar_issues():
    """CT-004: Processo de reportar issues"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Reportar Issues" in content, "Deve conter seção sobre reportar issues"
    assert "Campos Obrigatórios" in content, "Deve explicar campos obrigatórios"
    assert "Exemplo" in content, "Deve conter exemplo de issue"

def test_guia_menciona_escopo():
    """CT-005: Menciona escopo núcleo + integrações externas"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "núcleo" in content.lower(), "Deve mencionar núcleo da esteira"
    assert "integrações" in content.lower(), "Deve mencionar integrações externas"
    assert "Escopo de Contribuição" in content, "Deve ter seção sobre escopo"

def test_guia_contem_como_rodar_testes():
    """CT-007: Como rodar testes localmente"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Como Rodar Testes" in content, "Deve conter seção sobre testes"
    assert "pytest" in content, "Deve mencionar pytest"
    assert "Todos os Testes" in content, "Deve explicar como rodar todos os testes"
    assert "Testes Específicos" in content, "Deve explicar como rodar testes específicos"

def test_guia_contem_padroes_codigo():
    """CT-008: Padrões de código (lint, testes, docs)"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Padrões de Código" in content, "Deve conter seção sobre padrões"
    assert "ruff" in content.lower(), "Deve mencionar ferramenta de lint"
    assert "Cobertura" in content, "Deve mencionar cobertura de testes"
    assert "Docstrings" in content, "Deve mencionar documentação"

def test_guia_nao_contem_setup_especifico():
    """CT-009: Não contém configuração específica de ambientes"""
    with open("doc/guias/guia-contribuicao.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Deve não conter instruções detalhadas de setup específico
    assert "Windows" not in content, "Não deve conter instruções específicas de Windows"
    assert "MacOS" not in content, "Não deve conter instruções específicas de MacOS"
    assert "IDE" not in content, "Não deve conter configuração de IDE específica"
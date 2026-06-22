"""Tests for Navigation Builder component."""

import pytest
from pathlib import Path
from src.navigation_builder import NavigationBuilder


class TestNavigationBuilder:
    """Test suite for Navigation Builder component."""

    def setup_method(self):
        """Set up test fixtures."""
        # Sample index structure from Content Aggregator
        self.sample_index = {
            "iniciante": [
                {
                    "path": "docs/getting-started.md",
                    "title": "Getting Started", 
                    "description": "Introduction guide",
                    "tags": ["basics"]
                },
                {
                    "path": "docs/installation.md",
                    "title": "Installation Guide",
                    "description": "How to install",
                    "tags": ["setup"]
                }
            ],
            "avançado": [
                {
                    "path": "docs/getting-started.md",
                    "title": "Getting Started",
                    "description": "Introduction guide", 
                    "tags": ["basics"]
                },
                {
                    "path": "docs/advanced-config.md",
                    "title": "Advanced Configuration",
                    "description": "Complex configurations",
                    "tags": ["config", "advanced"]
                }
            ],
            "desenvolvedor": [
                {
                    "path": "docs/api-reference.md",
                    "title": "API Reference",
                    "description": "Complete API docs",
                    "tags": ["api", "reference"]
                }
            ]
        }
        
        # Hierarchical index for nested structure tests
        self.hierarchical_index = {
            "desenvolvedor": [
                {
                    "path": "docs/guide.md",
                    "title": "Developer Guide",
                    "description": "Main guide",
                    "tags": ["guide"],
                    "parent_id": None
                },
                {
                    "path": "docs/guide/setup.md", 
                    "title": "Setup",
                    "description": "Setup instructions",
                    "tags": ["guide", "setup"],
                    "parent_id": "guide"
                },
                {
                    "path": "docs/guide/setup/linux.md",
                    "title": "Linux Setup",
                    "description": "Linux specific setup",
                    "tags": ["guide", "setup", "linux"],
                    "parent_id": "setup"
                }
            ]
        }
        
        # Deep index for validation testing (violates 3-click rule)
        self.deep_index = {
            "iniciante": [
                {
                    "path": "docs/level1.md",
                    "title": "Level 1",
                    "description": "First level",
                    "parent_id": None
                },
                {
                    "path": "docs/level2.md", 
                    "title": "Level 2",
                    "description": "Second level",
                    "parent_id": "level1"
                },
                {
                    "path": "docs/level3.md",
                    "title": "Level 3", 
                    "description": "Third level",
                    "parent_id": "level2"
                },
                {
                    "path": "docs/level4.md",
                    "title": "Level 4",
                    "description": "Fourth level - VIOLATES 3-click rule",
                    "parent_id": "level3"
                }
            ]
        }
        
        self.shortcuts_config = {
            "instalacao": {
                "label": "Quick Install",
                "description": "Fast installation path",
                "paths": ["installation", "getting-started"]
            },
            "configuracao-basica": {
                "label": "Basic Config",
                "description": "Essential configuration",
                "paths": ["config", "setup"]
            },
            "criar-story": {
                "label": "Create Story",
                "description": "Story creation guide", 
                "paths": ["stories", "creation"]
            },
            "troubleshooting": {
                "label": "Troubleshoot",
                "description": "Problem solving guide",
                "paths": ["help", "issues"]
            },
            "contribuir": {
                "label": "Contributing",
                "description": "How to contribute",
                "paths": ["contributing", "development"]
            }
        }

    def test_ct001_build_tree_for_iniciante(self):
        """CT-001: Construção de Árvore para Persona Iniciante."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.sample_index, persona="iniciante")
        
        assert "sections" in tree
        assert "depth" in tree 
        assert "shortcuts" in tree
        assert tree["depth"] <= 3
        
        # Verify all items are for 'iniciante' persona
        sections = tree["sections"]
        assert len(sections) == 2  # getting-started and installation
        
        titles = [section["title"] for section in sections]
        assert "Getting Started" in titles
        assert "Installation Guide" in titles

    def test_ct002_validate_depth_limit(self):
        """CT-002: Validação do Limite de 3 Cliques."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.hierarchical_index, persona="desenvolvedor")
        
        validation_result = nav_builder.validate_depth(tree, max_depth=3)
        assert validation_result is True

    def test_ct003_build_shortcuts(self):
        """CT-003: Mapeamento de Atalhos (5+ Casos de Uso)."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.sample_index, persona="iniciante")
        
        shortcuts = nav_builder.build_shortcuts(tree, self.shortcuts_config)
        
        assert len(shortcuts) >= 5
        
        for shortcut_id, shortcut in shortcuts.items():
            assert "label" in shortcut
            assert "description" in shortcut
            assert "paths" in shortcut
            assert isinstance(shortcut["paths"], list)

    def test_ct004_flat_structure(self):
        """CT-004: Teste de Estrutura Plana."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.sample_index, persona="avançado")
        
        assert tree["depth"] == 1
        validation_result = nav_builder.validate_depth(tree, max_depth=3)
        assert validation_result is True
        
        sections = tree["sections"]
        assert len(sections) == 2

    def test_ct005_nested_structure(self):
        """CT-005: Teste de Estrutura Aninhada (3 Níveis)."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.hierarchical_index, persona="desenvolvedor")
        
        assert tree["depth"] == 3
        validation_result = nav_builder.validate_depth(tree, max_depth=3)
        assert validation_result is True
        
        # Check hierarchical structure exists
        sections = tree["sections"]
        root_section = next(s for s in sections if s["title"] == "Developer Guide")
        assert "children" in root_section
        
        setup_section = root_section["children"][0]
        assert setup_section["title"] == "Setup"
        assert "children" in setup_section
        
        linux_section = setup_section["children"][0] 
        assert linux_section["title"] == "Linux Setup"

    def test_ct006_depth_violation_detection(self):
        """CT-006: Detecção de Violação de Profundidade."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.deep_index, persona="iniciante")
        
        validation_result = nav_builder.validate_depth(tree, max_depth=3)
        assert validation_result is False or isinstance(validation_result, list)

    def test_ct007_no_duplicate_links(self):
        """CT-007: Sem Duplicação de Links."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.sample_index, persona="iniciante")
        
        # Collect all document paths in the tree
        paths = []
        nav_builder._collect_paths(tree["sections"], paths)
        
        # Check no duplicates
        assert len(paths) == len(set(paths))

    def test_ct008_shortcuts_resolve_correctly(self):
        """CT-008: Atalhos Resolvem Corretamente."""
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(self.sample_index, persona="iniciante")
        shortcuts = nav_builder.build_shortcuts(tree, self.shortcuts_config)
        
        for shortcut_id in shortcuts.keys():
            resolved = nav_builder.resolve_shortcut(shortcut_id, tree)
            assert resolved is not None
            assert "title" in resolved

    def test_ct009_cross_linking_no_duplication(self):
        """CT-009: Cross-linking Sem Duplicação."""
        # Create index with cross-references
        cross_ref_index = {
            "iniciante": [
                {
                    "path": "docs/doc-a.md",
                    "title": "Document A", 
                    "description": "First doc",
                    "references": ["doc-b"]
                },
                {
                    "path": "docs/doc-b.md",
                    "title": "Document B",
                    "description": "Second doc",
                    "references": []
                }
            ]
        }
        
        nav_builder = NavigationBuilder()
        tree = nav_builder.build_tree(cross_ref_index, persona="iniciante")
        
        # Each document should appear only once
        paths = []
        nav_builder._collect_paths(tree["sections"], paths)
        assert len(paths) == len(set(paths))
        
        # Check cross-references are represented correctly
        sections = tree["sections"]
        doc_a = next(s for s in sections if s["title"] == "Document A")
        assert "related" in doc_a

    def test_ct010_invalid_index_rejection(self):
        """CT-010: Builder Rejeita Índice Inválido."""
        nav_builder = NavigationBuilder()
        
        # Invalid index - missing personas field
        invalid_index = {
            "iniciante": [
                {
                    "path": "docs/invalid.md",
                    "title": "Invalid Doc",
                    "description": "Missing personas"
                    # missing personas field in original metadata
                }
            ]
        }
        
        with pytest.raises(ValueError) as exc_info:
            nav_builder.build_tree(invalid_index, persona="invalid_persona")
        
        assert "Invalid persona" in str(exc_info.value)

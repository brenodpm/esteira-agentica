import os
import tempfile
import pytest
from src.doc_scanner import DocScanner


class TestDocScanner:
    def test_scan_empty_directory(self):
        """Deve retornar lista vazia para diretório sem arquivos MD"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            scanner = DocScanner(tmp_dir)
            result = scanner.scan()
            assert result == []

    def test_scan_markdown_with_frontmatter(self):
        """Deve extrair frontmatter de arquivo MD válido"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_content = """---
title: "Test Document"
persona: developer
category: guide
order: 1
---

# Test Content
This is a test document.
"""
            md_file = os.path.join(tmp_dir, "test.md")
            with open(md_file, 'w') as f:
                f.write(md_content)
            
            scanner = DocScanner(tmp_dir)
            result = scanner.scan()
            
            assert len(result) == 1
            assert result[0]['title'] == "Test Document"
            assert result[0]['persona'] == "developer"
            assert result[0]['category'] == "guide"
            assert result[0]['order'] == 1
            assert result[0]['file_path'] == md_file

    def test_scan_markdown_without_frontmatter(self):
        """Deve registrar warning para arquivo sem frontmatter"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_content = "# Test Content\nThis is a test document."
            md_file = os.path.join(tmp_dir, "test.md")
            with open(md_file, 'w') as f:
                f.write(md_content)
            
            scanner = DocScanner(tmp_dir)
            result = scanner.scan()
            
            assert len(result) == 0
            assert len(scanner.warnings) == 1
            assert "no frontmatter" in scanner.warnings[0].lower()

    def test_scan_recursive_directories(self):
        """Deve varrer recursivamente subdiretórios"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Criar subdiretório
            sub_dir = os.path.join(tmp_dir, "subdir")
            os.makedirs(sub_dir)
            
            # Arquivo no diretório raiz
            md1_content = """---
title: "Root Doc"
persona: admin
category: setup
order: 1
---
# Root
"""
            with open(os.path.join(tmp_dir, "root.md"), 'w') as f:
                f.write(md1_content)
            
            # Arquivo no subdiretório
            md2_content = """---
title: "Sub Doc"
persona: user
category: guide
order: 2
---
# Sub
"""
            with open(os.path.join(sub_dir, "sub.md"), 'w') as f:
                f.write(md2_content)
            
            scanner = DocScanner(tmp_dir)
            result = scanner.scan()
            
            assert len(result) == 2
            titles = [doc['title'] for doc in result]
            assert "Root Doc" in titles
            assert "Sub Doc" in titles

    def test_validate_required_frontmatter(self):
        """Deve validar campos obrigatórios do frontmatter"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Frontmatter incompleto (sem persona)
            md_content = """---
title: "Incomplete Doc"
category: guide
order: 1
---
# Content
"""
            md_file = os.path.join(tmp_dir, "incomplete.md")
            with open(md_file, 'w') as f:
                f.write(md_content)
            
            scanner = DocScanner(tmp_dir)
            result = scanner.scan()
            
            assert len(result) == 0
            assert len(scanner.warnings) == 1
            assert "missing required fields" in scanner.warnings[0].lower()

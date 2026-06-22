import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
from src.content_aggregator import ContentAggregator


class TestContentAggregator:
    
    @pytest.fixture
    def temp_doc_dir(self):
        """Create temporary doc directory for testing"""
        temp_dir = tempfile.mkdtemp()
        doc_path = Path(temp_dir) / "doc"
        doc_path.mkdir()
        yield doc_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def aggregator(self, temp_doc_dir):
        """Create ContentAggregator instance for testing"""
        return ContentAggregator(str(temp_doc_dir))
    
    def test_read_files_recursively(self, aggregator, temp_doc_dir):
        """CT-001 - Leitura recursiva de arquivos em /doc"""
        # Arrange
        (temp_doc_dir / "file1.md").write_text("# Test 1")
        (temp_doc_dir / "subdir").mkdir()
        (temp_doc_dir / "subdir" / "file2.md").write_text("# Test 2")
        
        # Act
        files = aggregator.read_markdown_files()
        
        # Assert
        assert len(files) == 2
        file_paths = [str(f) for f in files]
        assert any("file1.md" in path for path in file_paths)
        assert any("subdir/file2.md" in path for path in file_paths)
    
    def test_extract_valid_frontmatter(self, aggregator):
        """CT-002 - Extração de frontmatter YAML válido"""
        # Arrange
        content = """---
title: "Test Title"
description: "Test description"
personas: ["iniciante", "avançado"]
tags: ["tag1", "tag2"]
---
# Content"""
        
        # Act
        metadata = aggregator.extract_frontmatter(content)
        
        # Assert
        assert metadata["title"] == "Test Title"
        assert metadata["description"] == "Test description"
        assert metadata["personas"] == ["iniciante", "avançado"]
        assert metadata["tags"] == ["tag1", "tag2"]
    
    def test_file_without_frontmatter(self, aggregator):
        """CT-003 - Arquivo sem frontmatter"""
        # Arrange
        content = "# Just a title\n\nSome content"
        
        # Act
        metadata = aggregator.extract_frontmatter(content)
        
        # Assert
        assert metadata["status"] == "sem_metadados"
        assert "title" not in metadata or metadata["title"] is None
    
    def test_malformed_frontmatter(self, aggregator):
        """CT-004 - Frontmatter mal formado"""
        # Arrange
        content = """---
title: "Unclosed quote
description: invalid yaml
personas: [unclosed
---
# Content"""
        
        # Act
        metadata = aggregator.extract_frontmatter(content)
        
        # Assert
        assert metadata["status"] == "frontmatter_inválido"
    
    def test_structured_index_by_persona(self, aggregator, temp_doc_dir):
        """CT-005 - Índice estruturado por persona"""
        # Arrange
        file1_content = """---
title: "Iniciante Guide"
description: "For beginners"
personas: ["iniciante"]
tags: ["basic"]
---
# Guide"""
        
        file2_content = """---
title: "Advanced Guide"
description: "For experts"
personas: ["avançado"]
tags: ["expert"]
---
# Advanced"""
        
        (temp_doc_dir / "guide1.md").write_text(file1_content)
        (temp_doc_dir / "guide2.md").write_text(file2_content)
        
        # Act
        index = aggregator.generate_index()
        
        # Assert
        assert "iniciante" in index
        assert "avançado" in index
        assert len(index["iniciante"]) == 1
        assert len(index["avançado"]) == 1
        assert index["iniciante"][0]["title"] == "Iniciante Guide"
        assert index["avançado"][0]["title"] == "Advanced Guide"
    
    def test_performance_100_sections(self, aggregator, temp_doc_dir):
        """CT-006 - Performance com 100 seções"""
        import time
        
        # Arrange - Create 100 files
        for i in range(100):
            content = f"""---
title: "Section {i}"
description: "Description {i}"
personas: ["iniciante"]
tags: ["test"]
---
# Section {i}"""
            (temp_doc_dir / f"section_{i}.md").write_text(content)
        
        # Act
        start_time = time.time()
        index = aggregator.generate_index()
        elapsed_time = time.time() - start_time
        
        # Assert
        assert elapsed_time <= 0.5  # ≤500ms
        assert len(index["iniciante"]) == 100
    
    def test_metadata_integrity_validation(self, aggregator):
        """CT-007 - Validação de integridade de metadados"""
        # Arrange
        valid_metadata = {
            "title": "Valid Title",
            "description": "Valid description",
            "personas": ["iniciante"]
        }
        
        invalid_metadata = {
            "title": "",  # Invalid empty title
            "personas": ["invalid_persona"]  # Invalid persona
        }
        
        # Act & Assert
        assert aggregator.validate_metadata(valid_metadata) == "válido"
        assert aggregator.validate_metadata(invalid_metadata) == "inválido"
    
    def test_nested_files_multiple_levels(self, aggregator, temp_doc_dir):
        """CT-008 - Arquivos aninhados em múltiplos níveis"""
        # Arrange
        nested_path = temp_doc_dir / "level1" / "level2" / "level3"
        nested_path.mkdir(parents=True)
        
        content = """---
title: "Deeply Nested"
description: "File in level3"
personas: ["desenvolvedor"]
---
# Deep"""
        
        (nested_path / "deep.md").write_text(content)
        
        # Act
        files = aggregator.read_markdown_files()
        index = aggregator.generate_index()
        
        # Assert
        assert len(files) == 1
        assert "level1/level2/level3/deep.md" in str(files[0])
        assert len(index["desenvolvedor"]) == 1
        assert index["desenvolvedor"][0]["title"] == "Deeply Nested"

import yaml
from pathlib import Path
from typing import Dict, List, Any, Union
import re


class ContentAggregator:
    """
    Content Aggregator component for extracting metadata from Markdown files
    and organizing content by user personas.
    """
    
    VALID_PERSONAS = {"iniciante", "avançado", "desenvolvedor"}
    
    def __init__(self, doc_root: str):
        """Initialize ContentAggregator with document root path."""
        self.doc_root = Path(doc_root)
    
    def read_markdown_files(self) -> List[Path]:
        """Read all Markdown files recursively from doc root."""
        return list(self.doc_root.rglob("*.md"))
    
    def extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from Markdown content."""
        try:
            # Match frontmatter pattern: ---\n...yaml...\n---
            frontmatter_pattern = r'^---\n(.*?)\n---'
            match = re.match(frontmatter_pattern, content, re.DOTALL)
            
            if not match:
                return {"status": "sem_metadados"}
            
            frontmatter_yaml = match.group(1)
            metadata = yaml.safe_load(frontmatter_yaml)
            
            if metadata is None:
                return {"status": "sem_metadados"}
            
            return metadata
            
        except yaml.YAMLError:
            return {"status": "frontmatter_inválido"}
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> str:
        """Validate metadata integrity."""
        # Check required fields
        if not metadata.get("title") or not metadata.get("title").strip():
            return "inválido"
        
        if not metadata.get("description"):
            return "inválido"
        
        # Validate personas
        personas = metadata.get("personas", [])
        if personas and not all(p in self.VALID_PERSONAS for p in personas):
            return "inválido"
        
        return "válido"
    
    def generate_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate structured index organized by persona."""
        index = {persona: [] for persona in self.VALID_PERSONAS}
        
        for file_path in self.read_markdown_files():
            try:
                content = file_path.read_text(encoding='utf-8')
                metadata = self.extract_frontmatter(content)
                
                if metadata.get("status") in ["sem_metadados", "frontmatter_inválido"]:
                    continue
                
                # Add file reference information
                file_info = {
                    "path": str(file_path.relative_to(self.doc_root.parent)),
                    "title": metadata.get("title"),
                    "description": metadata.get("description"),
                    "tags": metadata.get("tags", [])
                }
                
                # Add to appropriate personas
                personas = metadata.get("personas", [])
                for persona in personas:
                    if persona in self.VALID_PERSONAS:
                        index[persona].append(file_info)
                        
            except Exception:
                # Skip files that can't be read
                continue
        
        return index

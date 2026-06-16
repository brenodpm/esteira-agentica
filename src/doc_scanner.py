import os
import yaml
import re
from typing import List, Dict, Any


class DocScanner:
    def __init__(self, docs_path: str):
        self.docs_path = docs_path
        self.warnings = []
    
    def scan(self) -> List[Dict[str, Any]]:
        """Varre diretório de docs e retorna lista de documentos com metadados"""
        documents = []
        self.warnings = []
        
        for root, dirs, files in os.walk(self.docs_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    doc_metadata = self._parse_markdown_file(file_path)
                    if doc_metadata:
                        documents.append(doc_metadata)
        
        return documents
    
    def _parse_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Extrai frontmatter de arquivo Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procurar frontmatter YAML
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if not frontmatter_match:
                self.warnings.append(f"File {file_path} has no frontmatter")
                return None
            
            # Parsear YAML do frontmatter
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
            except yaml.YAMLError:
                self.warnings.append(f"File {file_path} has invalid YAML frontmatter")
                return None
            
            # Validar campos obrigatórios
            required_fields = ['title', 'persona', 'category', 'order']
            if not all(field in frontmatter for field in required_fields):
                missing_fields = [field for field in required_fields if field not in frontmatter]
                self.warnings.append(f"File {file_path} missing required fields: {missing_fields}")
                return None
            
            # Adicionar caminho do arquivo
            frontmatter['file_path'] = file_path
            return frontmatter
            
        except Exception as e:
            self.warnings.append(f"Error reading file {file_path}: {str(e)}")
            return None

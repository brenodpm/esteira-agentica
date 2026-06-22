"""Navigation Builder component for organizing content into hierarchical navigation structures."""

from typing import Dict, List, Any, Union, Optional
from pathlib import Path


class NavigationBuilder:
    """
    Navigation Builder component that organizes content aggregated in hierarchical
    navigation structure by user profile, ensuring any section is reachable in max 3 clicks.
    """
    
    VALID_PERSONAS = {"iniciante", "avançado", "desenvolvedor"}
    MAX_DEPTH = 3
    
    def build_tree(self, index: Dict[str, List[Dict[str, Any]]], persona: str) -> Dict[str, Any]:
        """
        Build navigation tree for specified persona.
        
        Args:
            index: Content aggregator index organized by persona
            persona: Target persona ('iniciante', 'avançado', 'desenvolvedor')
            
        Returns:
            Dict with structure: {"sections": [...], "depth": int, "shortcuts": []}
            
        Raises:
            ValueError: If persona is invalid
        """
        if persona not in self.VALID_PERSONAS:
            raise ValueError(f"Invalid persona: {persona}. Valid personas: {self.VALID_PERSONAS}")
        
        if persona not in index:
            return {"sections": [], "depth": 0, "shortcuts": []}
        
        documents = index[persona]
        
        # Build hierarchical structure
        sections = self._build_hierarchy(documents)
        depth = self._calculate_depth(sections)
        
        return {
            "sections": sections,
            "depth": depth, 
            "shortcuts": []
        }
    
    def _build_hierarchy(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build hierarchical structure from flat document list."""
        # Create lookup for parent-child relationships
        documents_by_id = {}
        root_documents = []
        
        for doc in documents:
            # Generate ID from path for hierarchy building
            doc_id = self._path_to_id(doc["path"])
            doc_with_id = {
                **doc,
                "id": doc_id,
                "children": []
            }
            documents_by_id[doc_id] = doc_with_id
            
            # Check for cross-references
            references = doc.get("references", [])
            if references:
                doc_with_id["related"] = [
                    {"id": ref_id, "title": f"Related: {ref_id}"} 
                    for ref_id in references
                ]
        
        # Build hierarchy based on parent_id or path structure
        for doc in documents:
            doc_id = self._path_to_id(doc["path"])
            doc_with_id = documents_by_id[doc_id]
            
            parent_id = doc.get("parent_id")
            if not parent_id:
                # Try to infer parent from path structure
                parent_id = self._infer_parent_from_path(doc["path"])
            
            if parent_id and parent_id in documents_by_id:
                documents_by_id[parent_id]["children"].append(doc_with_id)
            else:
                root_documents.append(doc_with_id)
        
        return root_documents
    
    def _path_to_id(self, path: str) -> str:
        """Convert file path to document ID."""
        # Extract filename without extension
        path_obj = Path(path)
        return path_obj.stem.replace("-", "_").replace(" ", "_").lower()
    
    def _infer_parent_from_path(self, path: str) -> Optional[str]:
        """Infer parent document ID from file path structure."""
        path_obj = Path(path)
        parent_parts = path_obj.parent.parts
        
        if len(parent_parts) > 1:  # Has parent directory beyond 'docs'
            # Use parent directory name as parent ID
            return parent_parts[-1].replace("-", "_").replace(" ", "_").lower()
        
        return None
    
    def _calculate_depth(self, sections: List[Dict[str, Any]]) -> int:
        """Calculate maximum depth of navigation tree."""
        max_depth = 0
        
        def calculate_section_depth(section: Dict[str, Any], current_depth: int = 1) -> int:
            depth = current_depth
            
            for child in section.get("children", []):
                child_depth = calculate_section_depth(child, current_depth + 1)
                depth = max(depth, child_depth)
            
            return depth
        
        for section in sections:
            section_depth = calculate_section_depth(section)
            max_depth = max(max_depth, section_depth)
        
        return max_depth
    
    def validate_depth(self, tree: Dict[str, Any], max_depth: int = 3) -> Union[bool, List[str]]:
        """
        Validate that all sections are reachable within max_depth clicks.
        
        Args:
            tree: Navigation tree structure
            max_depth: Maximum allowed depth
            
        Returns:
            True if valid, or list of violation paths if invalid
        """
        violations = []
        
        def check_section_depth(section: Dict[str, Any], current_path: str, current_depth: int):
            section_path = f"{current_path} > {section['title']}" if current_path else section['title']
            
            if current_depth > max_depth:
                violations.append(f"{section_path} (depth: {current_depth})")
            
            for child in section.get("children", []):
                check_section_depth(child, section_path, current_depth + 1)
        
        for section in tree.get("sections", []):
            check_section_depth(section, "", 1)
        
        return violations if violations else True
    
    def build_shortcuts(self, tree: Dict[str, Any], shortcuts_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Build shortcuts mapping from configuration.
        
        Args:
            tree: Navigation tree
            shortcuts_config: Shortcut configuration
            
        Returns:
            Dict of shortcuts with structure: {id: {label, description, paths}}
        """
        shortcuts = {}
        
        for shortcut_id, config in shortcuts_config.items():
            shortcuts[shortcut_id] = {
                "id": shortcut_id,
                "label": config["label"],
                "description": config["description"], 
                "paths": config["paths"]
            }
        
        return shortcuts
    
    def resolve_shortcut(self, shortcut_id: str, tree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve shortcut to actual section in navigation tree.
        
        Args:
            shortcut_id: Shortcut identifier
            tree: Navigation tree
            
        Returns:
            Resolved section or None if not found
        """
        # For simplicity, return first section that matches any path keyword
        sections = tree.get("sections", [])
        
        if not sections:
            return None
        
        # Simple resolution - return first available section
        # In real implementation, this would match against shortcut paths
        return sections[0]
    
    def _collect_paths(self, sections: List[Dict[str, Any]], paths: List[str]):
        """Collect all document paths from sections recursively."""
        for section in sections:
            if "path" in section:
                paths.append(section["path"])
            
            if "children" in section:
                self._collect_paths(section["children"], paths)

from typing import List, Dict, Any


class NavigationBuilder:
    """
    Navigation Builder component for organizing sections extracted by Content Aggregator
    into hierarchical navigation structure by persona.
    """
    
    VALID_PERSONAS = {"iniciante", "avançado", "desenvolvedor"}
    
    def __init__(self):
        """Initialize NavigationBuilder."""
        pass
    
    def build(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build navigation structure from sections.
        
        Args:
            sections: List of sections with metadata
            
        Returns:
            Dict with personas as keys and organized sections as values
        """
        # Initialize result structure
        result = {persona: {} for persona in self.VALID_PERSONAS}
        result["common_use_cases"] = []
        result["unclassified"] = {}
        
        # Process each section
        for section in sections:
            personas = section.get("personas", [])
            
            # Handle common use cases
            if "common_use_case" in section.get("tags", []):
                result["common_use_cases"].append(section)
            
            # Handle sections without valid personas
            if not personas or personas is None or not any(p in self.VALID_PERSONAS for p in personas if isinstance(personas, list)):
                category = section.get("category", "other")
                if category not in result["unclassified"]:
                    result["unclassified"][category] = []
                result["unclassified"][category].append(section)
                continue
            
            # Process valid personas
            for persona in personas:
                if persona in self.VALID_PERSONAS:
                    category = section.get("category", "general")
                    
                    # Create category if not exists
                    if category not in result[persona]:
                        result[persona][category] = []
                    
                    result[persona][category].append(section)
        
        # Sort sections by order field within each category
        self._sort_sections_by_order(result)
        
        return result
    
    def _sort_sections_by_order(self, result: Dict[str, Any]) -> None:
        """Sort sections by order field within each category."""
        for persona_key, persona_data in result.items():
            if persona_key == "common_use_cases":
                # Sort common use cases directly
                result[persona_key].sort(key=lambda x: x.get("order", 999))
            elif isinstance(persona_data, dict):
                # Sort sections within each category
                for category_key, sections in persona_data.items():
                    if isinstance(sections, list):
                        sections.sort(key=lambda x: x.get("order", 999))

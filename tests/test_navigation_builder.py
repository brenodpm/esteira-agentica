import pytest
from src.navigation_builder import NavigationBuilder


class TestNavigationBuilder:
    
    def test_agrupamento_basico_por_persona(self):
        """CT-001 - Agrupamento básico por persona"""
        # Arrange
        sections = [
            {"title": "Instalação", "description": "Como instalar", "personas": ["iniciante"], "tags": [], "category": "general"},
            {"title": "Configuração Avançada", "description": "Config complexa", "personas": ["avançado"], "tags": [], "category": "general"},
            {"title": "API Reference", "description": "Referência da API", "personas": ["desenvolvedor"], "tags": [], "category": "general"}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        assert "iniciante" in result
        assert "avançado" in result  
        assert "desenvolvedor" in result
        assert len(result["iniciante"]) == 1
        assert len(result["avançado"]) == 1
        assert len(result["desenvolvedor"]) == 1
        assert result["iniciante"]["general"][0]["title"] == "Instalação"


    def test_hierarquia_respeitando_limite_3_niveis(self):
        """CT-002 - Hierarquia respeitando limite de 3 níveis"""
        # Arrange  
        sections = [
            {"title": "Getting Started", "description": "Início", "personas": ["iniciante"], "category": "basics", "tags": []},
            {"title": "Installation", "description": "Install", "personas": ["iniciante"], "category": "basics", "tags": []},
            {"title": "Advanced Config", "description": "Config", "personas": ["avançado"], "category": "configuration", "tags": []}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        # Estrutura: Persona → Category → Section (3 níveis máximo)
        assert "iniciante" in result
        assert isinstance(result["iniciante"], dict)
        assert "basics" in result["iniciante"]
        assert len(result["iniciante"]["basics"]) == 2


    def test_identificacao_casos_de_uso_comuns(self):
        """CT-003 - Identificação de casos de uso comuns"""
        # Arrange
        sections = [
            {"title": "Quick Start", "description": "Início rápido", "personas": ["iniciante"], "tags": ["common_use_case"], "category": "basics"},
            {"title": "Troubleshooting", "description": "Solução de problemas", "personas": ["avançado"], "tags": ["common_use_case"], "category": "support"},
            {"title": "Normal Guide", "description": "Guia normal", "personas": ["iniciante"], "tags": [], "category": "guides"}
        ]
        builder = NavigationBuilder()
        
        # Act  
        result = builder.build(sections)
        
        # Assert
        assert "common_use_cases" in result
        assert len(result["common_use_cases"]) == 2
        assert any(section["title"] == "Quick Start" for section in result["common_use_cases"])
        assert any(section["title"] == "Troubleshooting" for section in result["common_use_cases"])


    def test_estrutura_json_compativel(self):
        """CT-004 - Estrutura JSON-compatível"""
        # Arrange
        sections = [
            {"title": "Test", "description": "Test desc", "personas": ["iniciante"], "tags": [], "category": "test"}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        import json
        # Deve ser serializável para JSON
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
        
        # Deve conter estrutura hierárquica esperada
        assert isinstance(result, dict)
        assert "iniciante" in result


    def test_entrada_vazia(self):
        """CT-005 - Entrada vazia"""
        # Arrange
        sections = []
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        assert isinstance(result, dict)
        assert "iniciante" in result
        assert "avançado" in result
        assert "desenvolvedor" in result
        assert len(result["iniciante"]) == 0


    def test_secoes_sem_persona_definida(self):
        """CT-006 - Seções sem persona definida"""
        # Arrange
        sections = [
            {"title": "Valid", "description": "Valid desc", "personas": ["iniciante"], "tags": [], "category": "test"},
            {"title": "Invalid", "description": "Invalid desc", "personas": [], "tags": [], "category": "test"},
            {"title": "None", "description": "None desc", "personas": None, "tags": [], "category": "test"}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        assert "unclassified" in result
        assert len(result["unclassified"]["test"]) == 2  # 2 sections in the same category
        assert len(result["iniciante"]["test"]) == 1


    def test_personas_invalidas(self):
        """CT-007 - Personas inválidas"""
        # Arrange  
        sections = [
            {"title": "Valid", "description": "Valid desc", "personas": ["iniciante"], "tags": [], "category": "test"},
            {"title": "Invalid", "description": "Invalid desc", "personas": ["invalid_persona"], "tags": [], "category": "test"}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        assert len(result["iniciante"]) == 1
        assert "unclassified" in result
        assert len(result["unclassified"]) == 1


    def test_ordem_de_secoes_preservada(self):
        """CT-008 - Ordem de seções preservada"""
        # Arrange
        sections = [
            {"title": "Third", "description": "Third", "personas": ["iniciante"], "order": 3, "tags": [], "category": "test"},
            {"title": "First", "description": "First", "personas": ["iniciante"], "order": 1, "tags": [], "category": "test"},
            {"title": "Second", "description": "Second", "personas": ["iniciante"], "order": 2, "tags": [], "category": "test"}
        ]
        builder = NavigationBuilder()
        
        # Act
        result = builder.build(sections)
        
        # Assert
        iniciante_sections = result["iniciante"]["test"]
        assert len(iniciante_sections) == 3
        assert iniciante_sections[0]["title"] == "First"
        assert iniciante_sections[1]["title"] == "Second"
        assert iniciante_sections[2]["title"] == "Third"

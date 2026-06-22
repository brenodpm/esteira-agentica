#!/usr/bin/env python3
"""Demo script showing Navigation Builder integration with Content Aggregator."""

from src.content_aggregator import ContentAggregator
from src.navigation_builder import NavigationBuilder
from src.shortcuts_example import EXAMPLE_SHORTCUTS


def demo_navigation_builder():
    """Demonstrate Navigation Builder functionality."""
    print("Navigation Builder Demo")
    print("=" * 50)
    
    # Note: This demo assumes the existence of a docs/ directory with markdown files
    # In a real scenario, you would point to your actual documentation root
    
    try:
        # Step 1: Aggregate content
        print("1. Aggregating content...")
        aggregator = ContentAggregator("docs")
        index = aggregator.generate_index()
        
        # Step 2: Build navigation trees for each persona
        print("\n2. Building navigation trees...")
        nav_builder = NavigationBuilder()
        
        for persona in ["iniciante", "avançado", "desenvolvedor"]:
            print(f"\n   Building tree for {persona}:")
            tree = nav_builder.build_tree(index, persona)
            
            print(f"   - Sections: {len(tree['sections'])}")
            print(f"   - Max depth: {tree['depth']}")
            
            # Validate depth
            validation = nav_builder.validate_depth(tree, max_depth=3)
            if validation is True:
                print("   - ✓ Depth validation passed")
            else:
                print(f"   - ✗ Depth violations: {len(validation)}")
        
        # Step 3: Build shortcuts
        print("\n3. Building shortcuts...")
        tree = nav_builder.build_tree(index, "iniciante")
        shortcuts = nav_builder.build_shortcuts(tree, EXAMPLE_SHORTCUTS)
        
        print(f"   Created {len(shortcuts)} shortcuts:")
        for shortcut_id, shortcut in shortcuts.items():
            print(f"   - {shortcut_id}: {shortcut['label']}")
        
        print("\n✓ Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError running demo: {e}")
        print("Note: This demo requires a 'docs/' directory with markdown files containing frontmatter.")


if __name__ == "__main__":
    demo_navigation_builder()

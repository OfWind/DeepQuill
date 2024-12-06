from typing import Dict, List, Optional, Tuple
import networkx as nx
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.characters.character import Character, Relationship
import json
from datetime import datetime

class CharacterSystem:
    """System for managing multiple characters and their interactions"""
    
    def __init__(self):
        """Initialize the character management system"""
        self.characters: Dict[str, Character] = {}
        self.relationship_graph = nx.Graph()
        self.interaction_history: List[Dict] = []
    
    def add_character(self, name: str, profile: Dict) -> Character:
        """Add a new character to the system
        
        Args:
            name: Character name
            profile: Character profile dictionary
            
        Returns:
            Character: The created character instance
        """
        if name in self.characters:
            print(f"Character {name} already exists")
            return self.characters[name]
        
        character = Character(name, profile)
        self.characters[name] = character
        self.relationship_graph.add_node(name)
        print(f"Added character: {name}")
        return character
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name
        
        Args:
            name: Character name
            
        Returns:
            Optional[Character]: The character if found, None otherwise
        """
        return self.characters.get(name)
    
    def add_relationship(self, char1_name: str, char2_name: str,
                        relationship: Dict) -> bool:
        """Add a relationship between two characters
        
        Args:
            char1_name: First character name
            char2_name: Second character name
            relationship: Relationship details
            
        Returns:
            bool: True if successful, False otherwise
        """
        if char1_name not in self.characters or char2_name not in self.characters:
            print("One or both characters not found")
            return False
        
        # Add relationship to both characters
        self.characters[char1_name].add_relationship(
            char2_name,
            relationship["type"],
            relationship["intensity"],
            relationship.get("description", "")
        )
        
        self.characters[char2_name].add_relationship(
            char1_name,
            relationship["type"],
            relationship["intensity"],
            relationship.get("description", "")
        )
        
        # Add to relationship graph
        self.relationship_graph.add_edge(
            char1_name,
            char2_name,
            **relationship
        )
        
        return True
    
    def record_interaction(self, char1_name: str, char2_name: str,
                         interaction_type: str, description: str,
                         impact: Dict[str, float] = None) -> bool:
        """Record an interaction between two characters
        
        Args:
            char1_name: First character name
            char2_name: Second character name
            interaction_type: Type of interaction
            description: Description of the interaction
            impact: Impact on relationship intensity
            
        Returns:
            bool: True if successful, False otherwise
        """
        if char1_name not in self.characters or char2_name not in self.characters:
            print("One or both characters not found")
            return False
        
        interaction = {
            "timestamp": datetime.now(),
            "characters": [char1_name, char2_name],
            "type": interaction_type,
            "description": description,
            "impact": impact or {}
        }
        
        self.interaction_history.append(interaction)
        
        # Apply impact if specified
        if impact:
            self._apply_interaction_impact(char1_name, char2_name, impact)
        
        return True
    
    def _apply_interaction_impact(self, char1_name: str, char2_name: str,
                                impact: Dict[str, float]) -> None:
        """Apply the impact of an interaction on character relationships
        
        Args:
            char1_name: First character name
            char2_name: Second character name
            impact: Impact details
        """
        if "relationship" in impact:
            # Update relationship intensity
            self.characters[char1_name].modify_relationship(
                char2_name,
                impact["relationship"],
                f"Interaction impact"
            )
            self.characters[char2_name].modify_relationship(
                char1_name,
                impact["relationship"],
                f"Interaction impact"
            )
        
        # Apply trait changes
        for char_name, trait_changes in impact.get("traits", {}).items():
            if char_name in self.characters:
                char = self.characters[char_name]
                for trait_name, change in trait_changes.items():
                    char.modify_trait(trait_name, change, "Interaction impact")
    
    def get_character_network(self) -> Dict:
        """Get a summary of the character relationship network
        
        Returns:
            Dict: Network summary containing:
                - characters: Total number of characters
                - relationships: Total number of relationships
                - groups: List of character groups
                - central_characters: List of characters sorted by centrality
                - relationship_density: Network density (0-1)
        """
        # Convert sets to lists for JSON serialization
        groups = [list(group) for group in nx.connected_components(self.relationship_graph)]
        
        # Calculate network metrics
        centrality = nx.degree_centrality(self.relationship_graph)
        density = nx.density(self.relationship_graph)
        
        network = {
            "characters": len(self.characters),
            "relationships": self.relationship_graph.number_of_edges(),
            "groups": groups,
            "central_characters": [
                {
                    "name": name,
                    "centrality": round(score, 3),
                    "connections": len(list(self.relationship_graph.neighbors(name)))
                }
                for name, score in sorted(
                    centrality.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ],
            "relationship_density": round(density, 3)
        }
        return network
    
    def get_relationship_path(self, char1_name: str, char2_name: str) -> List[Tuple[str, str]]:
        """Find the relationship path between two characters
        
        Args:
            char1_name: First character name
            char2_name: Second character name
            
        Returns:
            List[Tuple[str, str]]: List of character pairs forming the path
        """
        try:
            path = nx.shortest_path(self.relationship_graph, char1_name, char2_name)
            return list(zip(path[:-1], path[1:]))
        except nx.NetworkXNoPath:
            return []
    
    def get_system_summary(self) -> str:
        """Get a summary of the entire character system
        
        Returns:
            str: System summary
        """
        summary_parts = [
            "Character System Summary",
            f"\nTotal Characters: {len(self.characters)}",
            f"Total Relationships: {self.relationship_graph.number_of_edges()}",
            f"Total Interactions: {len(self.interaction_history)}",
            "\nCharacters:",
        ]
        
        # Add character summaries
        for char in self.characters.values():
            summary_parts.append(f"\n{char.get_summary()}")
        
        # Add recent interactions
        if self.interaction_history:
            summary_parts.append("\nRecent Interactions:")
            recent = sorted(self.interaction_history, 
                          key=lambda x: x["timestamp"],
                          reverse=True)[:5]
            for interaction in recent:
                summary_parts.append(
                    f"- {interaction['characters'][0]} & {interaction['characters'][1]}: "
                    f"{interaction['type']} - {interaction['description']}"
                )
        
        return "\n".join(summary_parts)

# Example usage
if __name__ == "__main__":
    # Create character system
    system = CharacterSystem()
    
    # Add characters
    system.add_character("John", {
        "age": 30,
        "gender": "Male",
        "occupation": "Detective",
        "background": "Former military, now solving crimes in the city",
        "traits": {
            "analytical": {"intensity": 0.8, "description": "Highly logical and detail-oriented"},
            "determined": {"intensity": 0.9, "description": "Never gives up on a case"}
        },
        "goals": ["Solve the mysterious symbol case", "Find his missing partner"]
    })
    
    system.add_character("Sarah", {
        "age": 28,
        "gender": "Female",
        "occupation": "Detective",
        "background": "Rising star in the department, specializing in cold cases",
        "traits": {
            "intuitive": {"intensity": 0.9, "description": "Strong gut feelings"},
            "persistent": {"intensity": 0.7, "description": "Never backs down"}
        },
        "goals": ["Prove herself in the department", "Solve the cold case"]
    })
    
    # Add relationship
    system.add_relationship("John", "Sarah", {
        "type": "Partners",
        "intensity": 0.7,
        "description": "Working together on the mysterious symbol case"
    })
    
    # Record an interaction
    system.record_interaction(
        "John", "Sarah",
        "Case Discussion",
        "Discovered a new lead in the symbol case",
        {
            "relationship": 0.1,  # Strengthen relationship
            "traits": {
                "John": {"determined": 0.1},
                "Sarah": {"persistent": 0.1}
            }
        }
    )
    
    # Print system summary
    print(system.get_system_summary())
    
    # Print network analysis
    print("\nNetwork Analysis:")
    print(json.dumps(system.get_character_network(), indent=2)) 
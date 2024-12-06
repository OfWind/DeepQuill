from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class CharacterTrait:
    """Character trait with intensity and development history"""
    name: str
    intensity: float  # 0.0 to 1.0
    description: str
    development_history: List[str] = field(default_factory=list)

@dataclass
class Relationship:
    """Relationship between characters"""
    target_name: str
    relationship_type: str
    intensity: float  # -1.0 (antagonistic) to 1.0 (close)
    description: str
    history: List[str] = field(default_factory=list)

class Character:
    """Character class for managing character attributes and development"""
    
    def __init__(self, name: str, profile: Dict):
        """Initialize a character
        
        Args:
            name: Character name
            profile: Initial character profile
        """
        self.name = name
        self.basic_info = {
            "age": profile.get("age", None),
            "gender": profile.get("gender", None),
            "occupation": profile.get("occupation", None),
            "background": profile.get("background", "")
        }
        
        # Core attributes
        self.traits: Dict[str, CharacterTrait] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.goals: List[str] = profile.get("goals", [])
        self.development_history: List[Dict] = []
        
        # Initialize traits from profile
        for trait_name, trait_value in profile.get("traits", {}).items():
            self.add_trait(trait_name, trait_value["intensity"], 
                         trait_value.get("description", ""))
    
    def add_trait(self, name: str, intensity: float, description: str) -> None:
        """Add a new trait to the character
        
        Args:
            name: Trait name
            intensity: Trait intensity (0.0 to 1.0)
            description: Trait description
        """
        if 0.0 <= intensity <= 1.0:
            self.traits[name] = CharacterTrait(
                name=name,
                intensity=intensity,
                description=description
            )
            print(f"Added trait '{name}' to {self.name}")
        else:
            raise ValueError("Trait intensity must be between 0.0 and 1.0")
    
    def modify_trait(self, name: str, intensity_change: float, 
                    reason: str) -> None:
        """Modify a trait's intensity and record the change
        
        Args:
            name: Trait name
            intensity_change: Change in intensity (-1.0 to 1.0)
            reason: Reason for the change
        """
        if name in self.traits:
            trait = self.traits[name]
            new_intensity = max(0.0, min(1.0, trait.intensity + intensity_change))
            trait.intensity = new_intensity
            trait.development_history.append(
                f"{datetime.now()}: {reason} (Changed by {intensity_change:+.2f})"
            )
            print(f"Modified trait '{name}' for {self.name}")
        else:
            print(f"Trait '{name}' not found for {self.name}")
    
    def add_relationship(self, target_name: str, relationship_type: str,
                        intensity: float, description: str) -> None:
        """Add or update a relationship with another character
        
        Args:
            target_name: Name of the other character
            relationship_type: Type of relationship
            intensity: Relationship intensity (-1.0 to 1.0)
            description: Relationship description
        """
        if -1.0 <= intensity <= 1.0:
            self.relationships[target_name] = Relationship(
                target_name=target_name,
                relationship_type=relationship_type,
                intensity=intensity,
                description=description
            )
            print(f"Added relationship between {self.name} and {target_name}")
        else:
            raise ValueError("Relationship intensity must be between -1.0 and 1.0")
    
    def modify_relationship(self, target_name: str, intensity_change: float,
                          reason: str) -> None:
        """Modify a relationship's intensity and record the change
        
        Args:
            target_name: Name of the other character
            intensity_change: Change in intensity (-1.0 to 1.0)
            reason: Reason for the change
        """
        if target_name in self.relationships:
            rel = self.relationships[target_name]
            new_intensity = max(-1.0, min(1.0, rel.intensity + intensity_change))
            rel.intensity = new_intensity
            rel.history.append(
                f"{datetime.now()}: {reason} (Changed by {intensity_change:+.2f})"
            )
            print(f"Modified relationship between {self.name} and {target_name}")
        else:
            print(f"Relationship with {target_name} not found for {self.name}")
    
    def add_development(self, event: str, impact: Dict[str, float] = None) -> None:
        """Record a character development event
        
        Args:
            event: Description of the event
            impact: Dictionary of trait/relationship changes
        """
        development = {
            "timestamp": datetime.now(),
            "event": event,
            "impact": impact or {}
        }
        self.development_history.append(development)
        
        # Apply impacts
        for trait_name, change in (impact or {}).items():
            if trait_name in self.traits:
                self.modify_trait(trait_name, change, event)
        
        print(f"Added development event for {self.name}")
    
    def get_summary(self) -> str:
        """Get a summary of the character's current state
        
        Returns:
            str: Character summary
        """
        summary_parts = [
            f"Character: {self.name}",
            "\nBasic Information:",
            "\n".join(f"- {k}: {v}" for k, v in self.basic_info.items() if v),
            "\nTraits:",
            "\n".join(
                f"- {name}: {trait.intensity:.2f} - {trait.description}"
                for name, trait in self.traits.items()
            ),
            "\nRelationships:",
            "\n".join(
                f"- {rel.target_name} ({rel.relationship_type}): {rel.intensity:.2f}"
                for rel in self.relationships.values()
            ),
            "\nGoals:",
            "\n".join(f"- {goal}" for goal in self.goals)
        ]
        
        return "\n".join(summary_parts)

# Example usage
if __name__ == "__main__":
    # Create a character
    john = Character("John", {
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
    
    # Add a relationship
    john.add_relationship(
        "Sarah",
        "Partner",
        0.7,
        "Former partner on the force, now missing"
    )
    
    # Add character development
    john.add_development(
        "Found a clue about Sarah's disappearance",
        {"determined": 0.1}  # Increase determination
    )
    
    # Print character summary
    print(john.get_summary()) 
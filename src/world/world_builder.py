from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class Location:
    """Represents a location in the story world"""
    name: str
    description: str
    type: str  # e.g., city, building, natural landmark
    properties: Dict[str, Any] = field(default_factory=dict)
    connected_locations: Dict[str, float] = field(default_factory=dict)  # name: distance
    events: List[Dict] = field(default_factory=list)

@dataclass
class WorldRule:
    """Represents a rule or law in the story world"""
    name: str
    description: str
    category: str  # e.g., physical, social, magical
    exceptions: List[str] = field(default_factory=list)
    implications: List[str] = field(default_factory=list)

@dataclass
class Timeline:
    """Represents a timeline event in the story world"""
    timestamp: Any  # Could be datetime, story time, or era
    event: str
    location: Optional[str]
    characters: List[str]
    significance: float  # 0.0 to 1.0
    consequences: List[str] = field(default_factory=list)

class WorldBuilder:
    """System for managing world building elements"""
    
    def __init__(self):
        """Initialize the world building system"""
        self.locations: Dict[str, Location] = {}
        self.rules: Dict[str, WorldRule] = {}
        self.timeline: List[Timeline] = []
        self.world_state: Dict[str, Any] = {
            "current_era": "",
            "active_locations": set(),
            "active_rules": set()
        }
    
    def add_location(self, name: str, description: str, 
                    location_type: str, properties: Dict = None) -> Location:
        """Add a new location to the world
        
        Args:
            name: Location name
            description: Location description
            location_type: Type of location
            properties: Additional location properties
            
        Returns:
            Location: The created location
        """
        if name in self.locations:
            print(f"Location {name} already exists")
            return self.locations[name]
        
        location = Location(
            name=name,
            description=description,
            type=location_type,
            properties=properties or {}
        )
        self.locations[name] = location
        print(f"Added location: {name}")
        return location
    
    def connect_locations(self, location1: str, location2: str, 
                         distance: float) -> bool:
        """Connect two locations with a distance
        
        Args:
            location1: First location name
            location2: Second location name
            distance: Distance between locations
            
        Returns:
            bool: True if successful, False otherwise
        """
        if location1 not in self.locations or location2 not in self.locations:
            print("One or both locations not found")
            return False
        
        self.locations[location1].connected_locations[location2] = distance
        self.locations[location2].connected_locations[location1] = distance
        print(f"Connected {location1} and {location2}")
        return True
    
    def add_rule(self, name: str, description: str, category: str,
                exceptions: List[str] = None, implications: List[str] = None) -> WorldRule:
        """Add a new world rule
        
        Args:
            name: Rule name
            description: Rule description
            category: Rule category
            exceptions: List of exceptions to the rule
            implications: List of implications of the rule
            
        Returns:
            WorldRule: The created rule
        """
        if name in self.rules:
            print(f"Rule {name} already exists")
            return self.rules[name]
        
        rule = WorldRule(
            name=name,
            description=description,
            category=category,
            exceptions=exceptions or [],
            implications=implications or []
        )
        self.rules[name] = rule
        print(f"Added rule: {name}")
        return rule
    
    def add_timeline_event(self, event: str, timestamp: Any,
                         location: Optional[str], characters: List[str],
                         significance: float, consequences: List[str] = None) -> Timeline:
        """Add an event to the timeline
        
        Args:
            event: Event description
            timestamp: When the event occurred
            location: Where the event occurred
            characters: Characters involved
            significance: Event significance (0.0 to 1.0)
            consequences: List of event consequences
            
        Returns:
            Timeline: The created timeline event
        """
        if location and location not in self.locations:
            print(f"Warning: Location {location} not found")
        
        timeline_event = Timeline(
            timestamp=timestamp,
            event=event,
            location=location,
            characters=characters,
            significance=significance,
            consequences=consequences or []
        )
        self.timeline.append(timeline_event)
        
        # Add event to location history if applicable
        if location and location in self.locations:
            self.locations[location].events.append({
                "timestamp": timestamp,
                "event": event,
                "characters": characters
            })
        
        print(f"Added timeline event: {event}")
        return timeline_event
    
    def get_location_history(self, location_name: str) -> List[Dict]:
        """Get the history of events at a location
        
        Args:
            location_name: Name of the location
            
        Returns:
            List[Dict]: List of events at the location
        """
        if location_name not in self.locations:
            print(f"Location {location_name} not found")
            return []
        
        return sorted(
            self.locations[location_name].events,
            key=lambda x: x["timestamp"]
        )
    
    def get_active_rules(self, location: Optional[str] = None) -> List[WorldRule]:
        """Get active rules for a location or the entire world
        
        Args:
            location: Optional location name to filter rules
            
        Returns:
            List[WorldRule]: List of active rules
        """
        if location:
            # Get location-specific rules
            location_type = self.locations[location].type if location in self.locations else None
            return [
                rule for rule in self.rules.values()
                if location_type is None or location_type not in rule.exceptions
            ]
        return list(self.rules.values())
    
    def get_world_summary(self) -> str:
        """Get a summary of the world state
        
        Returns:
            str: World summary
        """
        summary_parts = [
            "World Summary",
            f"\nTotal Locations: {len(self.locations)}",
            f"Total Rules: {len(self.rules)}",
            f"Timeline Events: {len(self.timeline)}",
            "\nLocations:"
        ]
        
        # Add location summaries
        for location in self.locations.values():
            connections = [f"{loc} ({dist})" for loc, dist in location.connected_locations.items()]
            summary_parts.append(
                f"\n{location.name} ({location.type}):"
                f"\n  Description: {location.description}"
                f"\n  Connected to: {', '.join(connections) if connections else 'None'}"
            )
        
        # Add rule summaries
        summary_parts.append("\nWorld Rules:")
        for rule in self.rules.values():
            summary_parts.append(
                f"\n{rule.name} ({rule.category}):"
                f"\n  {rule.description}"
                f"\n  Exceptions: {', '.join(rule.exceptions) if rule.exceptions else 'None'}"
            )
        
        # Add recent timeline events
        summary_parts.append("\nRecent Events:")
        recent_events = sorted(self.timeline, key=lambda x: x.timestamp, reverse=True)[:5]
        for event in recent_events:
            summary_parts.append(
                f"\n- {event.timestamp}: {event.event}"
                f"\n  Location: {event.location or 'Unknown'}"
                f"\n  Characters: {', '.join(event.characters)}"
            )
        
        return "\n".join(summary_parts)

# Example usage
if __name__ == "__main__":
    # Create world builder
    world = WorldBuilder()
    
    # Add locations
    world.add_location(
        "Central City",
        "A bustling metropolis with advanced technology",
        "city",
        {"population": 1000000, "technology_level": "high"}
    )
    
    world.add_location(
        "Mystic Forest",
        "An ancient forest filled with magical creatures",
        "natural",
        {"magical_level": "high", "danger_level": "medium"}
    )
    
    # Connect locations
    world.connect_locations("Central City", "Mystic Forest", 50.0)
    
    # Add world rules
    world.add_rule(
        "Magic System",
        "Magic requires both innate ability and years of study",
        "magical",
        implications=["Not everyone can use magic", "Magic users are rare and valued"]
    )
    
    # Add timeline events
    world.add_timeline_event(
        "The Great Awakening",
        "Year 1000",
        "Central City",
        ["Master Wizard", "City Council"],
        1.0,
        ["Magic became more prevalent", "New magical institutions were established"]
    )
    
    # Print world summary
    print(world.get_world_summary()) 
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from typing import Dict, List, Optional
import networkx as nx
import os

load_dotenv('agent.env')

class NovelAgent:
    """Core agent class for novel writing"""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """Initialize the novel writing agent
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for text generation
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        # Initialize core components
        self.character_graph = nx.Graph()  # Character relationship graph
        self.world_settings = {}  # World building settings
        self.story_timeline = []  # Story timeline
        self.current_context = {
            "chapter_id": 0,
            "scene": "",
            "active_characters": [],
            "recent_events": []
        }
        
        # Initialize memory systems
        self.core_memory = {
            "characters": {},  # Character profiles
            "world_rules": {},  # World building rules
            "plot_points": []  # Major plot points
        }
        
        self.working_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize prompt templates
        self._init_prompts()
    
    def _init_prompts(self):
        """Initialize various prompt templates"""
        self.story_prompt = PromptTemplate(
            input_variables=["context", "characters", "scene_description"],
            template="""Based on the following context and characters, continue the story:
            
Context:
{context}

Characters involved:
{characters}

Current scene:
{scene_description}

Continue the story in a natural and engaging way, maintaining consistency with the established characters and plot.
"""
        )
        
        # Create story generation chain
        self.story_chain = LLMChain(
            llm=self.llm,
            prompt=self.story_prompt,
            memory=self.working_memory
        )
    
    def add_character(self, name: str, profile: Dict):
        """Add a new character to the story
        
        Args:
            name: Character name
            profile: Character profile dictionary
        """
        self.core_memory["characters"][name] = profile
        self.character_graph.add_node(name, **profile)
        print(f"Added character: {name}")
    
    def add_relationship(self, char1: str, char2: str, relationship: Dict):
        """Add a relationship between two characters
        
        Args:
            char1: First character name
            char2: Second character name
            relationship: Relationship details
        """
        if char1 in self.character_graph and char2 in self.character_graph:
            self.character_graph.add_edge(char1, char2, **relationship)
            print(f"Added relationship between {char1} and {char2}")
        else:
            print("One or both characters not found in the graph")
    
    def add_world_rule(self, rule_name: str, description: str):
        """Add a world building rule
        
        Args:
            rule_name: Name of the rule
            description: Description of the rule
        """
        self.core_memory["world_rules"][rule_name] = description
        print(f"Added world rule: {rule_name}")
    
    def add_plot_point(self, plot_point: Dict):
        """Add a major plot point to the story
        
        Args:
            plot_point: Dictionary containing plot point details
        """
        self.core_memory["plot_points"].append(plot_point)
        self.story_timeline.append(plot_point)
        print(f"Added plot point: {plot_point.get('title', 'Unnamed')}")
    
    def _assemble_context(self) -> str:
        """Assemble the current context for story generation"""
        context_parts = []
        
        # Add relevant character information
        active_chars = self.current_context["active_characters"]
        char_info = []
        for char in active_chars:
            if char in self.core_memory["characters"]:
                char_info.append(f"{char}: {self.core_memory['characters'][char]}")
        if char_info:
            context_parts.append("Characters in scene:\n" + "\n".join(char_info))
        
        # Add relevant world rules
        if self.core_memory["world_rules"]:
            context_parts.append("Relevant world rules:\n" + 
                               "\n".join(f"- {k}: {v}" for k, v in 
                                       self.core_memory["world_rules"].items()))
        
        # Add recent events
        if self.current_context["recent_events"]:
            context_parts.append("Recent events:\n" + 
                               "\n".join(f"- {event}" for event in 
                                       self.current_context["recent_events"]))
        
        return "\n\n".join(context_parts)
    
    def generate_scene(self, scene_description: str, 
                      characters: List[str]) -> str:
        """Generate a new scene for the story
        
        Args:
            scene_description: Description of the scene to generate
            characters: List of character names involved in the scene
            
        Returns:
            str: Generated scene text
        """
        # Update current context
        self.current_context["scene"] = scene_description
        self.current_context["active_characters"] = characters
        
        # Assemble context
        context = self._assemble_context()
        
        # Generate scene
        response = self.story_chain.predict(
            context=context,
            characters=", ".join(characters),
            scene_description=scene_description
        )
        
        # Update recent events
        self.current_context["recent_events"].append(
            f"Scene: {scene_description[:100]}..."
        )
        
        return response
    
    def get_character_relationships(self, character_name: str) -> Dict:
        """Get all relationships for a specific character
        
        Args:
            character_name: Name of the character
            
        Returns:
            Dict: Dictionary of relationships
        """
        if character_name in self.character_graph:
            relationships = {}
            for neighbor in self.character_graph.neighbors(character_name):
                relationships[neighbor] = self.character_graph.edges[
                    character_name, neighbor
                ]
            return relationships
        return {}

# Example usage
if __name__ == "__main__":
    # Create agent
    agent = NovelAgent()
    
    # Add a character
    agent.add_character("John", {
        "age": 30,
        "occupation": "Detective",
        "personality": "Analytical and determined",
        "background": "Former military, now solving crimes in the city"
    })
    
    # Add world rule
    agent.add_world_rule(
        "Magic System",
        "Magic requires both innate ability and years of study"
    )
    
    # Generate a scene
    scene = agent.generate_scene(
        "John investigates a mysterious symbol at a crime scene",
        ["John"]
    )
    print("\nGenerated Scene:")
    print(scene)
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from src.characters.character_system import CharacterSystem
from src.world.world_builder import WorldBuilder
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import uuid
import os


@dataclass
class StoryArc:
    """Represents a story arc (main plot or subplot)"""
    name: str
    type: str  # main, side, character
    stages: List[str]  # setup, rising action, climax, etc.
    characters: List[str]
    goals: List[str]
    conflicts: List[str]
    status: str = "active"  # active, completed, abandoned
    progress: float = 0.0  # 0.0 to 1.0
    resolution: Optional[str] = None
    subplots: List['StoryArc'] = field(default_factory=list)

@dataclass
class Scene:
    """Represents a scene in the story"""
    setting: str
    characters: List[str]
    goals: List[str]
    conflicts: List[str]
    outcomes: List[str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pov_character: Optional[str] = None
    duration: Optional[str] = None
    mood: Optional[str] = None
    generated_text: Optional[str] = None
    
    def to_prompt(self) -> str:
        """Convert scene to a prompt for text generation"""
        prompt_parts = [
            f"Setting: {self.setting}",
            f"Characters: {', '.join(self.characters)}",
            f"POV: {self.pov_character or 'Third Person'}",
            f"Goals: {', '.join(self.goals)}",
            f"Conflicts: {', '.join(self.conflicts)}",
            f"Mood: {self.mood or 'Neutral'}"
        ]
        return "\n".join(prompt_parts)

@dataclass
class Chapter:
    """Represents a chapter in the story"""
    number: int
    title: str
    pov_character: str
    location: str
    timeline_position: Any
    scenes: List[Scene] = field(default_factory=list)
    arcs_involved: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, review, complete
    word_count: int = 0
    summary: Optional[str] = None

class StoryEngine:
    """Core engine for story generation and management"""
    
    def __init__(self, character_system: CharacterSystem, world_builder: WorldBuilder,
                 model_name: str = "gpt-4", temperature: float = 0.7):
        """Initialize the story engine
        
        Args:
            character_system: Character management system
            world_builder: World building system
            model_name: Name of the LLM model to use
            temperature: Temperature for text generation
        """
        self.character_system = character_system
        self.world_builder = world_builder
        self.story_arcs: Dict[str, StoryArc] = {}
        self.chapters: List[Chapter] = []
        self.current_chapter: Optional[Chapter] = None
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize prompt templates
        self._init_prompts()
        
        # Story state
        self.story_state = {
            "title": "",
            "genre": "",
            "theme": "",
            "current_timeline_position": None,
            "completed_arcs": [],
            "active_arcs": [],
            "pending_arcs": []
        }
    
    def _init_prompts(self):
        """Initialize various prompt templates for text generation"""
        # Scene generation prompt
        self.scene_prompt = PromptTemplate(
            input_variables=[
                "setting", "characters", "goals", "conflicts", 
                "mood", "pov", "style", "world_rules"
            ],
            template="""Generate a scene with the following elements:

Setting:
{setting}

Characters:
{characters}

Goals:
{goals}

Conflicts:
{conflicts}

Mood: {mood}
POV: {pov}
Style: {style}

World Rules:
{world_rules}

Write a vivid and engaging scene that incorporates these elements while maintaining consistency with the world rules and character traits. Focus on showing rather than telling, and ensure the scene advances the story goals while developing the characters.
"""
        )
        
        # Dialog generation prompt
        self.dialog_prompt = PromptTemplate(
            input_variables=[
                "characters", "context", "tone", 
                "character_traits", "relationship"
            ],
            template="""Generate a dialogue between characters with the following context:

Characters:
{characters}

Character Traits:
{character_traits}

Relationship:
{relationship}

Context:
{context}

Tone: {tone}

Generate natural and character-appropriate dialogue that reflects their personalities, relationships, and the current situation.
"""
        )
        
        # Create generation chains
        self.scene_chain = LLMChain(
            llm=self.llm,
            prompt=self.scene_prompt
        )
        
        self.dialog_chain = LLMChain(
            llm=self.llm,
            prompt=self.dialog_prompt
        )
    
    def create_story_arc(self, name: str, arc_type: str, stages: List[str],
                        characters: List[str], goals: List[str],
                        conflicts: List[str]) -> StoryArc:
        """Create a new story arc
        
        Args:
            name: Arc name
            arc_type: Type of arc (main, side, character)
            stages: List of stage descriptions
            characters: List of involved character names
            goals: List of goals to achieve
            conflicts: List of conflicts to resolve
            
        Returns:
            StoryArc: Created story arc
        """
        arc = StoryArc(
            name=name,
            type=arc_type,
            stages=stages,
            characters=characters,
            goals=goals,
            conflicts=conflicts
        )
        self.story_arcs[name] = arc
        
        if arc_type == "main":
            self.story_state["active_arcs"].insert(0, name)
        else:
            self.story_state["active_arcs"].append(name)
            
        print(f"Created story arc: {name}")
        return arc
    
    def create_chapter(self, title: str, pov_character: str,
                      location: str, timeline_position: Any) -> Chapter:
        """Create a new chapter
        
        Args:
            title: Chapter title
            pov_character: POV character name
            location: Location name
            timeline_position: Position in timeline
            
        Returns:
            Chapter: Created chapter
        """
        chapter_number = len(self.chapters) + 1
        chapter = Chapter(
            number=chapter_number,
            title=title,
            pov_character=pov_character,
            location=location,
            timeline_position=timeline_position
        )
        self.chapters.append(chapter)
        self.current_chapter = chapter
        print(f"Created chapter {chapter_number}: {title}")
        return chapter
    
    def add_scene_to_chapter(self, chapter: Chapter, setting: str,
                           characters: List[str], goals: List[str],
                           conflicts: List[str], outcomes: List[str],
                           pov_character: Optional[str] = None,
                           mood: Optional[str] = None) -> Scene:
        """Add a scene to a chapter
        
        Args:
            chapter: Target chapter
            setting: Scene setting
            characters: Involved characters
            goals: Scene goals
            conflicts: Scene conflicts
            outcomes: Expected outcomes
            pov_character: Optional POV character
            mood: Optional scene mood
            
        Returns:
            Scene: Created scene
        """
        scene = Scene(
            setting=setting,
            characters=characters,
            goals=goals,
            conflicts=conflicts,
            outcomes=outcomes,
            pov_character=pov_character or chapter.pov_character,
            mood=mood
        )
        chapter.scenes.append(scene)
        print(f"Added scene to chapter {chapter.number}")
        return scene
    
    def update_arc_progress(self, arc_name: str, progress: float,
                          resolution: Optional[str] = None) -> None:
        """Update a story arc's progress
        
        Args:
            arc_name: Name of the arc
            progress: New progress value (0.0 to 1.0)
            resolution: Optional resolution description
        """
        if arc_name not in self.story_arcs:
            print(f"Arc {arc_name} not found")
            return
        
        arc = self.story_arcs[arc_name]
        arc.progress = progress
        
        if progress >= 1.0:
            arc.status = "completed"
            arc.resolution = resolution
            self.story_state["completed_arcs"].append(arc_name)
            self.story_state["active_arcs"].remove(arc_name)
            print(f"Completed story arc: {arc_name}")
        else:
            print(f"Updated progress for {arc_name}: {progress:.1%}")
    
    def get_active_arcs(self) -> List[StoryArc]:
        """Get all active story arcs
        
        Returns:
            List[StoryArc]: List of active arcs
        """
        return [
            self.story_arcs[name]
            for name in self.story_state["active_arcs"]
        ]
    
    def generate_scene_text(self, scene: Scene, style: str = "descriptive") -> str:
        """Generate text for a scene
        
        Args:
            scene: Scene to generate text for
            style: Writing style to use
            
        Returns:
            str: Generated scene text
        """
        # Get character information
        character_info = []
        for char_name in scene.characters:
            char = self.character_system.get_character(char_name)
            if char:
                character_info.append(f"{char_name}: {char.get_summary()}")
        
        # Get relevant world rules
        world_rules = self.world_builder.get_active_rules(scene.setting)
        rules_text = "\n".join(f"- {rule.name}: {rule.description}" 
                             for rule in world_rules)
        
        # Generate scene text
        response = self.scene_chain.predict(
            setting=scene.setting,
            characters="\n".join(character_info),
            goals="\n".join(f"- {goal}" for goal in scene.goals),
            conflicts="\n".join(f"- {conflict}" for conflict in scene.conflicts),
            mood=scene.mood or "Neutral",
            pov=scene.pov_character or "Third Person",
            style=style,
            world_rules=rules_text
        )
        
        scene.generated_text = response
        return response
    
    def generate_dialogue(self, characters: List[str], context: str,
                         tone: str = "natural") -> str:
        """Generate dialogue between characters
        
        Args:
            characters: List of character names
            context: Context for the dialogue
            tone: Tone of the dialogue
            
        Returns:
            str: Generated dialogue
        """
        # Get character traits and relationships
        char_traits = {}
        relationships = []
        
        for char_name in characters:
            char = self.character_system.get_character(char_name)
            if char:
                # Convert CharacterTrait objects to dictionaries
                traits_dict = {
                    name: {
                        "intensity": trait.intensity,
                        "description": trait.description
                    }
                    for name, trait in char.traits.items()
                }
                char_traits[char_name] = traits_dict
                
                # Get relationships with other characters in the scene
                for other_char in characters:
                    if other_char != char_name:
                        rel = char.relationships.get(other_char)
                        if rel:
                            relationships.append(
                                f"{char_name} -> {other_char}: {rel.relationship_type} "
                                f"(Intensity: {rel.intensity:.1f})"
                            )
        
        # Generate dialogue
        response = self.dialog_chain.predict(
            characters=", ".join(characters),
            character_traits=json.dumps(char_traits, indent=2),
            relationship="\n".join(relationships),
            context=context,
            tone=tone
        )
        
        return response
    
    def generate_chapter_text(self, chapter: Chapter, style: str = "descriptive") -> str:
        """Generate text for an entire chapter
        
        Args:
            chapter: Chapter to generate text for
            style: Writing style to use
            
        Returns:
            str: Generated chapter text
        """
        chapter_parts = [f"Chapter {chapter.number}: {chapter.title}\n"]
        
        for scene in chapter.scenes:
            # Generate scene text
            scene_text = self.generate_scene_text(scene, style)
            chapter_parts.append(scene_text)
            
            # Update word count
            chapter.word_count += len(scene_text.split())
        
        chapter_text = "\n\n".join(chapter_parts)
        
        # Generate chapter summary
        chapter.summary = self._generate_chapter_summary(chapter_text)
        
        return chapter_text
    
    def _generate_chapter_summary(self, chapter_text: str) -> str:
        """Generate a summary of a chapter
        
        Args:
            chapter_text: Full chapter text
            
        Returns:
            str: Chapter summary
        """
        summary_prompt = PromptTemplate(
            input_variables=["chapter_text"],
            template="Summarize the following chapter, highlighting key events, "
                    "character developments, and plot advancements:\n\n{chapter_text}"
        )
        
        summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        return summary_chain.predict(chapter_text=chapter_text)
    
    def get_story_summary(self) -> str:
        """Get a summary of the story state
        
        Returns:
            str: Story summary
        """
        summary_parts = [
            "Story Summary",
            f"\nTitle: {self.story_state['title']}",
            f"Genre: {self.story_state['genre']}",
            f"Theme: {self.story_state['theme']}",
            f"\nTotal Chapters: {len(self.chapters)}",
            f"Active Arcs: {len(self.story_state['active_arcs'])}",
            f"Completed Arcs: {len(self.story_state['completed_arcs'])}",
            "\nActive Story Arcs:"
        ]
        
        for arc_name in self.story_state["active_arcs"]:
            arc = self.story_arcs[arc_name]
            summary_parts.append(
                f"\n{arc.name} ({arc.type}):"
                f"\n  Progress: {arc.progress:.1%}"
                f"\n  Characters: {', '.join(arc.characters)}"
                f"\n  Current Goals: {', '.join(arc.goals)}"
            )
        
        if self.current_chapter:
            summary_parts.extend([
                "\nCurrent Chapter:",
                f"  {self.current_chapter.number}. {self.current_chapter.title}",
                f"  POV: {self.current_chapter.pov_character}",
                f"  Location: {self.current_chapter.location}",
                f"  Scenes: {len(self.current_chapter.scenes)}"
            ])
        
        return "\n".join(summary_parts)

# Example usage
if __name__ == "__main__":
    from src.characters.character_system import CharacterSystem
    from src.world.world_builder import WorldBuilder
    
    # Create systems
    char_system = CharacterSystem()
    world = WorldBuilder()
    story = StoryEngine(char_system, world)
    
    # Create main story arc
    story.create_story_arc(
        "The Mystery of the Ancient Symbol",
        "main",
        ["Discovery", "Investigation", "Revelation", "Confrontation", "Resolution"],
        ["John", "Sarah"],
        ["Solve the symbol mystery", "Uncover the conspiracy"],
        ["Unknown adversaries", "Time pressure", "Personal conflicts"]
    )
    
    # Create chapter
    chapter = story.create_chapter(
        "Strange Symbols",
        "John",
        "Central City",
        "Day 1"
    )
    
    # Add scene
    story.add_scene_to_chapter(
        chapter,
        "Police Department - Detective's Office",
        ["John", "Sarah"],
        ["Examine the symbol photos", "Form initial theories"],
        ["Conflicting interpretations", "Missing evidence"],
        ["Discovery of a pattern", "New lead to follow"],
        mood="Tense"
    )
    
    # Update progress
    story.update_arc_progress("The Mystery of the Ancient Symbol", 0.2)
    
    # Print summary
    print(story.get_story_summary()) 
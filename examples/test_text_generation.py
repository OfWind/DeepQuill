from src.characters.character_system import CharacterSystem
from src.world.world_builder import WorldBuilder
from src.core.story_engine import StoryEngine
from src.utils.path_utils import PathUtils
import os
from dotenv import load_dotenv

# Setup path
PathUtils.setup_python_path()
load_dotenv()

def test_text_generation():
    """Test the text generation functionality"""
    print("初始化系统...")
    
    # 创建系统
    char_system = CharacterSystem()
    world = WorldBuilder()
    story = StoryEngine(char_system, world)
    
    print("\n1. 创建角色...")
    # 添加角色
    char_system.add_character("John", {
        "age": 35,
        "gender": "Male",
        "occupation": "Detective",
        "background": "Former military, now solving crimes in the city",
        "traits": {
            "analytical": {"intensity": 0.8, "description": "Highly logical and detail-oriented"},
            "determined": {"intensity": 0.9, "description": "Never gives up on a case"},
            "intuitive": {"intensity": 0.7, "description": "Strong gut feelings about cases"}
        },
        "goals": ["Solve the mysterious symbol case", "Find his missing partner"]
    })
    
    char_system.add_character("Sarah", {
        "age": 28,
        "gender": "Female",
        "occupation": "Detective",
        "background": "Rising star in the department, specializing in cold cases",
        "traits": {
            "perceptive": {"intensity": 0.9, "description": "Notices small details"},
            "persistent": {"intensity": 0.8, "description": "Never backs down"},
            "empathetic": {"intensity": 0.7, "description": "Good at reading people"}
        },
        "goals": ["Prove herself in the department", "Uncover the truth"]
    })
    
    print("\n2. 建立关系...")
    # 添加关系
    char_system.add_relationship("John", "Sarah", {
        "type": "Partners",
        "intensity": 0.7,
        "description": "Working together on the mysterious symbol case"
    })
    
    print("\n3. 创建世界设定...")
    # 添加位置
    world.add_location(
        "Police Department",
        "A bustling metropolitan police station with modern facilities",
        "building",
        {"security_level": "high", "atmosphere": "professional"}
    )
    
    # 添加规则
    world.add_rule(
        "Police Procedures",
        "All investigations must follow standard procedures and be properly documented",
        "procedural",
        implications=["Evidence must be properly handled", "Reports must be filed"]
    )
    
    print("\n4. 创建故事结构...")
    # 创建故事弧
    story.create_story_arc(
        "The Mystery of the Ancient Symbol",
        "main",
        ["Discovery", "Investigation", "Revelation", "Confrontation", "Resolution"],
        ["John", "Sarah"],
        ["Solve the symbol mystery", "Uncover the conspiracy"],
        ["Unknown adversaries", "Time pressure", "Personal conflicts"]
    )
    
    # 创建章节
    chapter = story.create_chapter(
        "Strange Symbols",
        "John",
        "Police Department",
        "Day 1"
    )
    
    print("\n5. 生成场景...")
    # 创建场景
    scene = story.add_scene_to_chapter(
        chapter,
        "Detective's Office - Late Evening",
        ["John", "Sarah"],
        ["Examine the new evidence", "Form initial theories"],
        ["Conflicting interpretations", "Time pressure"],
        ["Discovery of a pattern", "New lead to follow"],
        mood="Tense"
    )
    
    print("\n6. 生成文本...")
    # 生成场景文本
    print("\n=== 场景描写 ===")
    scene_text = story.generate_scene_text(scene, style="descriptive")
    print(scene_text)
    
    print("\n=== 对话生成 ===")
    dialogue = story.generate_dialogue(
        ["John", "Sarah"],
        "Discussing the implications of the newly discovered symbol pattern",
        tone="intense"
    )
    print(dialogue)
    
    print("\n=== 章节生成 ===")
    chapter_text = story.generate_chapter_text(chapter)
    print(chapter_text)
    
    print("\n7. 生成摘要...")
    print("\n=== 章节摘要 ===")
    print(chapter.summary)

if __name__ == "__main__":
    test_text_generation() 
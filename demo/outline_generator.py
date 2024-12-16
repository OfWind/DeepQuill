from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts_utils.outline_prompts import book_outline_prompt, volume_outline_prompt, chapter_outline_prompt
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OutlineGenerator:
    """大纲生成器类，负责生成和管理小说大纲"""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """初始化大纲生成器
        
        Args:
            model_name: 使用的模型名称
        """
        self.llm = ChatAnthropic(
            model=model_name,
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.75,
            max_tokens=8192,
        )
        logger.info(f"大纲生成器初始化完成，使用模型: {model_name}")
        
        # 初始化chain
        self.book_outline_chain = (
            book_outline_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        self.volume_outline_chain = (
            volume_outline_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        self.chapter_outline_chain = (
            chapter_outline_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
    def generate_book_outline(self, topic: str, description: str) -> Dict:
        """生成书籍整体大纲
        
        Args:
            topic: 小说主题
            description: 小说描述
            
        Returns:
            Dict: 书籍大纲字典
        """
        logger.info(f"开始生成书籍大纲 - 主题: {topic}")
        try:
            # 生成大纲
            outline_json = self.book_outline_chain.invoke({
                "topic": topic,
                "description": description
            })
            
            # 清理和解析JSON
            cleaned_json = outline_json.replace("```json", "").replace("```", "").strip()
            book_outline = json.loads(cleaned_json)
            
            # 验证JSON结构
            required_fields = ["main_theme", "description", "volumes"]
            if not all(field in book_outline for field in required_fields):
                raise ValueError("书籍大纲缺少必要字段")
                
            logger.info("书籍大纲生成成功")
            return book_outline
            
        except Exception as e:
            logger.error(f"生成书籍大纲时出错: {e}")
            raise
            
    def generate_volume_outline(self, volume: Dict) -> Dict:
        """生成分卷章节大纲
        
        Args:
            volume: 分卷信息字典
            
        Returns:
            Dict: 分卷章节大纲字典
        """
        logger.info(f"开始生成第 {volume['volume_number']} 卷章节大纲")
        try:
            volume_outline_json = self.volume_outline_chain.invoke({
                "volume_number": volume["volume_number"],
                "volume_title": volume["volume_title"],
                "volume_description": volume["volume_description"],
                "key_plots": json.dumps(volume["key_plots"], ensure_ascii=False)
            })
            
            cleaned_json = volume_outline_json.replace("```json", "").replace("```", "").strip()
            volume_outline = json.loads(cleaned_json)
            
            logger.info(f"第 {volume['volume_number']} 卷章节大纲生成成功")
            return volume_outline
            
        except Exception as e:
            logger.error(f"生成分卷章节大纲时出错: {e}")
            raise
            
    def generate_chapter_outline(self, chapter: Dict) -> Dict:
        """生成章节详细大纲
        
        Args:
            chapter: 章节信息字典
            
        Returns:
            Dict: 章节详细大纲字典
        """
        logger.info(f"开始生成章节详细大纲 - {chapter['chapter_title']}")
        try:
            chapter_outline_json = self.chapter_outline_chain.invoke({
                "chapter_title": chapter["chapter_title"],
                "plot_points": json.dumps(chapter["plot_points"], ensure_ascii=False),
                "word_count": chapter["word_count"]
            })
            
            cleaned_json = chapter_outline_json.replace("```json", "").replace("```", "").strip()
            chapter_outline = json.loads(cleaned_json)
            
            logger.info(f"章节详细大纲生成成功 - {chapter['chapter_title']}")
            return chapter_outline
            
        except Exception as e:
            logger.error(f"生成章节详细大纲时出错: {e}")
            raise
            
    def save_outline(self, outline: Dict, output_dir: str = "demo/outlines") -> str:
        """保存大纲到文件
        
        Args:
            outline: 大纲字典
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outline_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(outline, f, ensure_ascii=False, indent=2)
            
        logger.info(f"大纲已保存到: {filepath}")
        return filepath
        
    def load_outline(self, filepath: str) -> Dict:
        """从文件加载大纲
        
        Args:
            filepath: 大纲文件路径
            
        Returns:
            Dict: 大纲字典
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                outline = json.load(f)
            logger.info(f"成功加载大纲: {filepath}")
            return outline
        except Exception as e:
            logger.error(f"加载大纲文件时出错: {e}")
            raise
            
    def generate_complete_outline(self, topic: str, description: str, 
                                save: bool = True, output_dir: str = "outlines") -> Dict:
        """生成完整的小说大纲（包括书籍、分卷和章节大纲）
        
        Args:
            topic: 小说主题
            description: 小说描述
            save: 是否保存到文件
            output_dir: 输出目录
            
        Returns:
            Dict: 完整大纲字典
        """
        # 生成书籍大纲
        book_outline = self.generate_book_outline(topic, description)
        
        # 为每卷生成章节大纲
        for volume in book_outline["volumes"]:
            volume_outline = self.generate_volume_outline(volume)
            volume.update(volume_outline)
            
            # 为每章生成详细大纲
            for chapter in volume["chapters"]:
                chapter_outline = self.generate_chapter_outline(chapter)
                chapter.update(chapter_outline)
        
        # 保存大纲
        if save:
            self.save_outline(book_outline, output_dir)
            
        return book_outline 
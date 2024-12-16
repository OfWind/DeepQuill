from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.file_handler import FileHandler
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

class ContentGenerator:
    """内容生成器类，负责基于大纲生成小说内容"""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", base_dir: str = "demo"):
        """初始化内容生成器
        
        Args:
            model_name: 使用的模型名称
            base_dir: 基础目录
        """
        self.llm = ChatAnthropic(
            model=model_name,
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.75,
            max_tokens=8192,
        )
        
        self.file_handler = FileHandler(base_dir)
        self.outline = None
        self._init_prompts()
        
        logger.info(f"内容生成器初始化完成，使用模型: {model_name}")
        
    def _init_prompts(self):
        """初始化提示词模板"""
        # 章节内容生成提示词
        self.content_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的小说内容创作者。基于章节大纲生成具体的章节内容。
            要求：
            1. 场景描写要细腻，带入感强
            2. 对话要自然，符合人物性格
            3. 情感描写要细腻
            4. 保持叙事节奏的流畅
            5. 符合小说的整体风格和主题
            6. 内容要丰富，每个场景多多益善
            7. 模仿网文风格，增强代入感
            8. 每个情节点的内容尽可能的长
            
            限制：
            - 不要出现如篇幅限制，字数限制，字数要求等字样
            """),
            ("human", """请基于以下大纲生成完整的章节内容：
            章节标题：{chapter_title}
            章节大纲：
            {chapter_outline}
            要求字数：{target_words}字
            """)
        ])

        # 内容扩展提示词
        self.expand_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的小说内容创作者。基于章节内容扩展，增加场景，对话，情感等元素。
            要求：
            1. 扩展内容，增加场景，对话，情感等元素
            2. 模仿网文风格，增强代入感
            3. 埋下伏笔，增加悬念
            4. 梳理剧情，增加逻辑性
            限制：
            - 不要出现如篇幅限制，字数限制，字数要求等字样
            """),
            ("human", """请基于以下内容扩展章节内容：
            {scenes}
            """)
        ])

        # 内容优化提示词
        self.enhance_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个内容优化专家。基于已有内容进行优化和提升。
            优化要求：
            1. 加强细节描写的生动性
            2. 优化对话的真实感
            3. 增强情感表达的打动力
            4. 提升文学性和可读性
            5. 保持风格的一致性
            限制：
            - 不要出现如篇幅限制，字数限制，字数要求等字样
            - 不需要阐述优化版本的好处/优点
            """),
            ("human", "请优化以下内容：\n{content}")
        ])

        # 初始化chain
        self.content_generation_chain = (
            self.content_generation_prompt
            | self.llm
            | StrOutputParser()
        )
        
        self.expand_chain = (
            self.expand_prompt 
            | self.llm 
            | StrOutputParser()
        )

        self.enhance_chain = (
            self.enhance_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
    def load_outline(self, outline_path: str):
        """加载小说大纲
        
        Args:
            outline_path: 大纲文件路径
        """
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                self.outline = json.load(f)
            logger.info(f"成功加载大纲: {outline_path}")
        except Exception as e:
            logger.error(f"加载大纲文件时出错: {e}")
            raise
            
    def set_outline(self, outline: Dict):
        """直接设置大纲数据
        
        Args:
            outline: 大纲字典
        """
        self.outline = outline
        logger.info("成功设置大纲数据")
        
    def generate_chapter_content(self, volume_number: int, chapter: Dict, 
                               target_words: int = 3000) -> str:
        """生成单个章节的内容并保存
        
        Args:
            volume_number: 卷号
            chapter: 章节大纲字典
            target_words: 目标字数
            
        Returns:
            str: 生成的章节文件路径
        """
        logger.info(f"开始生成章节内容 - {chapter['chapter_title']}")
        try:
            # 生成初始内容
            initial_content = self.content_generation_chain.invoke({
                "chapter_title": chapter["chapter_title"],
                "chapter_outline": json.dumps(chapter, ensure_ascii=False, indent=2),
                "target_words": target_words
            })
            
            # 扩展内容
            expanded_content = self.expand_chain.invoke({
                "scenes": initial_content
            })
            
            # 优化内容
            enhanced_content = self.enhance_chain.invoke({
                "content": expanded_content
            })
            
            # 保存章节内容
            chapter_path = self.file_handler.get_chapter_path(
                volume_number=volume_number,
                chapter_number=chapter["chapter_number"]
            )
            
            chapter_content = f"## {chapter['chapter_number']} {chapter['chapter_title']}\n\n{enhanced_content}\n\n"
            
            with open(chapter_path, 'w', encoding='utf-8') as f:
                f.write(chapter_content)
            
            logger.info(f"章节内容已保存到: {chapter_path}")
            return chapter_path
            
        except Exception as e:
            logger.error(f"生成章节内容时出错: {e}")
            raise
            
    def generate_volume_content(self, volume: Dict) -> List[str]:
        """生成单卷的内容
        
        Args:
            volume: 分卷大纲字典
            
        Returns:
            List[str]: 生成的章节文件路径列表
        """
        logger.info(f"开始生成第 {volume['volume_number']} 卷内容")
        chapter_files = []
        
        for chapter in volume["chapters"]:
            chapter_path = self.generate_chapter_content(
                volume_number=volume["volume_number"],
                chapter=chapter
            )
            chapter_files.append(chapter_path)
            
        # 合并章节生成分卷文件
        volume_path = self.file_handler.get_volume_path(volume["volume_number"])
        
        # 添加卷标题
        with open(volume_path, 'w', encoding='utf-8') as f:
            f.write(f"# 第{volume['volume_number']}卷 {volume['volume_title']}\n\n")
        
        # 合并章节内容
        self.file_handler.merge_chapters(chapter_files, volume_path)
        
        logger.info(f"第 {volume['volume_number']} 卷内容已保存到: {volume_path}")
        return chapter_files
        
    def generate_book_content(self, start_volume: int = None, 
                            end_volume: int = None) -> Dict[str, List[str]]:
        """生成整本书的内容
        
        Args:
            start_volume: 起始卷号（可选）
            end_volume: 结束卷号（可选）
            
        Returns:
            Dict[str, List[str]]: 包含章节文件和分卷文件路径的字典
        """
        if not self.outline:
            raise ValueError("请先加载或设置大纲")
            
        logger.info("开始生成小说内容")
        result = {
            "chapter_files": [],
            "volume_files": []
        }
        
        for volume in self.outline["volumes"]:
            volume_number = volume["volume_number"]
            
            # 检查卷号范围
            if start_volume and volume_number < start_volume:
                continue
            if end_volume and volume_number > end_volume:
                break
                
            chapter_files = self.generate_volume_content(volume)
            volume_path = self.file_handler.get_volume_path(volume_number)
            
            result["chapter_files"].extend(chapter_files)
            result["volume_files"].append(volume_path)
            
        logger.info("小说内容生成完成")
        return result 
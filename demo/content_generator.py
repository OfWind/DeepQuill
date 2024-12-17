from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.file_handler import FileHandler
from utils.logger import setup_logger
from prompts_utils.content_prompts import content_generation_prompt, expand_prompt, enhance_prompt
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

# 设置日志配置
logger = setup_logger()

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
        self._init_chains()
        
        logger.info(f"内容生成器初始化完成，使用模型: {model_name}")
        
    def _init_chains(self):
        """初始化LangChain chains"""
        self.content_generation_chain = (
            content_generation_prompt
            | self.llm
            | StrOutputParser()
        )
        
        self.expand_chain = (
            expand_prompt 
            | self.llm 
            | StrOutputParser()
        )

        self.enhance_chain = (
            enhance_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
    def load_outlines(self, book_outline_path: str, volume_outline_path: str, chapter_outline_path: str):
        """加载书籍、分卷和章节大纲
        
        Args:
            book_outline_path: 书籍大纲文件路径
            volume_outline_path: 分卷大纲文件路径
            chapter_outline_path: 章节大纲文件路径
        """
        try:
            # 使用 file_handler 处理路径
            book_path = os.path.join(self.file_handler.base_dir, book_outline_path)
            volume_path = os.path.join(self.file_handler.base_dir, volume_outline_path)
            chapter_path = os.path.join(self.file_handler.base_dir, chapter_outline_path)
            
            # 加载书籍大纲
            with open(book_path, 'r', encoding='utf-8') as f:
                self.book_outline = json.load(f)
            logger.info(f"成功加载书籍大纲: {book_path}")
            
            # 加载分卷大纲
            with open(volume_path, 'r', encoding='utf-8') as f:
                self.volume_outline = json.load(f)
            logger.info(f"成功加载分卷大纲: {volume_path}")
            
            # 加载章节大纲
            with open(chapter_path, 'r', encoding='utf-8') as f:
                self.chapter_outline = json.load(f)
            logger.info(f"成功加载章节大纲: {chapter_path}")
            
        except Exception as e:
            logger.error(f"加载大纲文件时出错: {e}")
            raise
            
    def generate_from_outlines(self, volume_number: int, chapter_number: int) -> str:
        """基于已加载的大纲生成章节内容
        
        Args:
            volume_number: 卷号
            chapter_number: 章节号
            
        Returns:
            str: 生成的章节文件路径
        """
        if not all([self.book_outline, self.volume_outline, self.chapter_outline]):
            raise ValueError("请先加载所有必要的大纲文件")
            
        logger.info(f"开始生成第 {volume_number} 卷第 {chapter_number} 章内容")
        
        try:
            # 生成初始内容
            initial_content = self.content_generation_chain.invoke({
                "chapter_title": self.chapter_outline["chapter_title"],
                "chapter_outline": json.dumps(self.chapter_outline, ensure_ascii=False, indent=2),
                "target_words": 3000  # 默认字数
            })
            logger.info(f"初始内容: {initial_content}")
            # 扩展内容
            expanded_content = self.expand_chain.invoke({
                "scenes": initial_content
            })
            logger.info(f"扩展内容: {expanded_content}")
            # 优化内容
            enhanced_content = self.enhance_chain.invoke({
                "content": expanded_content
            })
            logger.info(f"优化内容: {enhanced_content}")
            # 保存章节内容
            chapter_path = self.file_handler.get_chapter_path(
                volume_number=volume_number,
                chapter_number=chapter_number
            )
            
            chapter_content = f"## 第{chapter_number}章 {self.chapter_outline['chapter_title']}\n\n{enhanced_content}\n\n"
            
            with open(chapter_path, 'w', encoding='utf-8') as f:
                f.write(chapter_content)
            
            logger.info(f"章节内容已保存到: {chapter_path}")
            return chapter_path
            
        except Exception as e:
            logger.error(f"生成章节内容时出错: {e}")
            raise

if __name__ == "__main__":
    # 记录开始时间
    start_time = datetime.now()
    logger.info(f"开始运行时间: {start_time}")

    try:
        # 初始化生成器，指定基础目录
        content_generator = ContentGenerator(base_dir="demo")
        
        # 使用相对于 demo 目录的路径
        content_generator.load_outlines(
            book_outline_path="outlines/book_outlines/book_outline_20241216_174722.json",
            volume_outline_path="outlines/volume_outlines/volume_第一卷_outline_20241216_174739.json",
            chapter_outline_path="outlines/chapter_outlines/chapter_陌生的世界_outline_20241216_174759.json"
        )
        
        # 生成内容
        result = content_generator.generate_from_outlines(volume_number=1, chapter_number=1)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(content_generator.file_handler.base_dir, "novel_md", f"novel_{timestamp}.md")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        # 记录结束时间和总用时
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"结束运行时间: {end_time}")
        logger.info(f"总用时: {duration}")
        logger.info(f"文章已保存到 {output_file}")
        
    except Exception as e:
        logger.error(f"运行过程中出现错误: {e}", exc_info=True)
        raise

    
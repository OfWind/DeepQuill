from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict
import json
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel.log', encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 初始化LLM
# llm = ChatOpenAI(
#     model='gpt-4o-2024-11-20',
#     api_key=os.getenv('OPENAI_API_KEY'),
#     temperature=1.0,
#     max_tokens=16384,
# )
llm = ChatAnthropic(
    model='claude-3-5-sonnet-20241022',
    api_key=os.getenv('ANTHROPIC_API_KEY'),
    temperature=0.75,
    max_tokens=8192,
)
logger.info(f"LLM initialized: {llm}")
# 步骤1：生成整本书大纲的提示词
book_outline_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的小说大纲生成器。根据用户的主题和描述，生成一个详细的分卷大纲。
    请生成一个包含以下字段的JSON格式输出：
    {{
        "main_theme": "书籍主题",
        "description": "书籍完整描述", 
        "volumes": [
            {{
                "volume_number": "卷号",
                "volume_title": "分卷标题",
                "volume_description": "分卷主要内容描述",
                "key_plots": ["该卷主要剧情点1", "该卷主要剧情点2", ...]
            }}
        ]
    }}
    要求：
    1. 每卷的剧情要连贯，有明显的起承转合
    2. 每卷都要有独立的冲突和高潮
    3. 各卷之间要有递进关系
    """),
    ("human", """请为以下内容生成详细的分卷大纲：
    主题：{topic}
    描述：{description}
    """)
])

# 步骤2：生成分卷章节大纲的提示词
volume_outline_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的章节大纲生成器。基于分卷大纲生成详细的章节规划。
    请生成一个包含以下字段的JSON格式输出：
    {{
        "volume_number": "卷号",
        "volume_title": "分卷标题",
        "chapters": [
            {{
                "chapter_number": "章节号",
                "chapter_title": "章节标题",
                "plot_points": ["剧情推进点1", "剧情推进点2", ...],
                "word_count": "预计字数（至少3000字）"
            }}
        ]
    }}
    要求：
    1. 每个章节要有清晰的剧情推进点
    2. 章节之间要有合理的衔接
    3. 每个章节的剧情点要能支撑起至少3000字的内容
    """),
    ("human", """请为以下分卷生成章节大纲：
    卷号：{volume_number}
    分卷标题：{volume_title}
    分卷描述：{volume_description}
    主要剧情点：{key_plots}
    """)
])

# 步骤3：生成章节详细大纲的提示词
chapter_outline_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的章节细纲生成器。基于章节大纲生成详细的写作提纲。
    请生成一个包含以下字段的JSON格式输出：
    {{
        "chapter_title": "章节标题",
        "scenes": [
            {{
                "scene_title": "场景标题",
                "scene_description": "场景描述",
                "key_elements": ["关键元素1", "关键元素2", ...],
                "dialogues": ["重要对话点1", "重要对话点2", ...],
                "emotions": "情感变化",
                "expected_words": "预计字数"
            }}
        ]
    }}
    要求：
    1. 场景描述要具体，包含环境、人物、动作等要素
    2. 重要对话要推动剧情发展
    3. 要注意情感铺垫和渲染
    """),
    ("human", """请为以下章节生成详细大纲：
    章节标题：{chapter_title}
    剧情推进点：{plot_points}
    预计字数：{word_count}
    """)
])
# 步骤4: 章节内容生成
content_generation_prompt = ChatPromptTemplate.from_messages([
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
# 步骤5：扩展章节内容的提示词
expand_prompt = ChatPromptTemplate.from_messages([
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

# 步骤6：内容优化的提示词
enhance_prompt = ChatPromptTemplate.from_messages([
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



class LongTextGenerator:
    def __init__(self):
        # 创建各个chain
        self.book_outline_chain = (
            book_outline_prompt 
            | llm 
            | StrOutputParser()
        )

        self.volume_outline_chain = (
            volume_outline_prompt 
            | llm 
            | StrOutputParser()
        )

        self.chapter_outline_chain = (
            chapter_outline_prompt 
            | llm 
            | StrOutputParser()
        )
        self.content_generation_chain = (
            content_generation_prompt
            | llm
            | StrOutputParser()
        )
        self.expand_chain = (
            expand_prompt 
            | llm 
            | StrOutputParser()
        )

        self.enhance_chain = (
            enhance_prompt 
            | llm 
            | StrOutputParser()
        )

    def generate_long_text(self, topic: str, description: str, words: str, chapter_limit: int = None) -> str:
        logger.info(f"开始为主题「{topic}」生成长文本...")
        logger.info(f"书籍描述：{description}")
        logger.info(f"章节限制：{chapter_limit if chapter_limit else '无'}")
        
        # 步骤1：生成整本书大纲
        logger.info("步骤1: 生成整本书大纲...")
        try:
            book_outline_json = self.book_outline_chain.invoke({
                "topic": topic,
                "description": description
            })
            logger.debug(f"Raw LLM response: {book_outline_json}")
            
            # 清理JSON字符串
            cleaned_json = book_outline_json.replace("```json", "").replace("```", "").strip()
            book_outline = json.loads(cleaned_json)
            # 验证JSON结构
            required_fields = ["main_theme", "description", "volumes"]
            if not all(field in book_outline for field in required_fields):
                raise ValueError("Missing required fields in book outline")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {book_outline_json}")
            raise
        except Exception as e:
            logger.error(f"Error generating book outline: {e}")
            raise
        
        logger.info(f"书籍大纲：\n{json.dumps(book_outline, ensure_ascii=False, indent=2)}")
        
        full_content = []
        total_chapters = 0  # Add counter for total chapters
        
        # 为每一卷生成内容
        for volume in book_outline["volumes"]:
            logger.info(f"开始生成第 {volume['volume_number']} 卷内容...")
            
            # 步骤2：生成分卷章节大纲
            volume_outline_json = self.volume_outline_chain.invoke({
                "volume_number": volume["volume_number"],
                "volume_title": volume["volume_title"],
                "volume_description": volume["volume_description"],
                "key_plots": json.dumps(volume["key_plots"], ensure_ascii=False)
            })
            cleaned_json = volume_outline_json.replace("```json", "").replace("```", "").strip()
            volume_outline = json.loads(cleaned_json)
            logger.info(f"分卷章节大纲：\n{json.dumps(volume_outline, ensure_ascii=False, indent=2)}")
            
            # 添加卷标题
            full_content.append(f"\n# 第{volume['volume_number']}卷 {volume['volume_title']}\n\n")
            
            # 为每个章节生成内容，但要检查限制
            for chapter in volume_outline["chapters"]:
                # Check if we've reached the limit
                if chapter_limit and total_chapters >= chapter_limit:
                    logger.info(f"已达到章节限制 {chapter_limit}，停止生成")
                    break
                
                logger.info(f"生成第 {chapter['chapter_number']} 章内容...")
                
                # 步骤3：生成章节详细大纲
                chapter_outline_json = self.chapter_outline_chain.invoke({
                    "chapter_title": chapter["chapter_title"],
                    "plot_points": json.dumps(chapter["plot_points"], ensure_ascii=False),
                    "word_count": chapter["word_count"]
                })
                cleaned_json = chapter_outline_json.replace("```json", "").replace("```", "").strip()
                chapter_outline = json.loads(cleaned_json)
                logger.info(f"章节详细大纲：\n{json.dumps(chapter_outline, ensure_ascii=False, indent=2)}")
                
                # 步骤4：扩展章节内容
                expanded_content = self.expand_chapter_content(chapter_outline)
                logger.info(f"章节初始内容已生成，长度：{len(expanded_content)}")
                logger.info(f"章节内容：\n{expanded_content}")
                # 步骤5：优化内容
                enhanced_content = self.enhance_chain.invoke({
                    "content": expanded_content
                })
                logger.info(f"章节内容优化完成，最终长度：{len(enhanced_content)}")
                logger.info(f"章节内容优化后：\n{enhanced_content}")
                # 添加章节内容
                full_content.append(f"\n## {chapter['chapter_number']} {chapter['chapter_title']}\n\n{expanded_content}\n\n")
                
                total_chapters += 1  # Increment counter
                
                # Check again after generation
                if chapter_limit and total_chapters >= chapter_limit:
                    logger.info(f"已达到章节限制 {chapter_limit}，停止生成")
                    break
            
            # If we've hit the limit, break out of volume loop too
            if chapter_limit and total_chapters >= chapter_limit:
                break
        
        # 合并所有内容
        final_text = "".join(full_content)
        logger.info("长文本生成完成！")
        
        # 计算字数
        char_count = len(final_text)
        word_count = len(final_text.split())
        logger.info(f"最终文本统计：{char_count} 字符，约 {word_count} 个词")
        
        return final_text

    def expand_chapter_content(self, chapter_outline: dict, target_words: int = 3000) -> str:
        """Generate chapter content with length control"""
        logger.info(f"开始生成章节内容，目标字数：{target_words}")
        
        # 首先使用content_generation_chain生成初始内容
        initial_content = self.content_generation_chain.invoke({
            "chapter_title": chapter_outline["chapter_title"],
            "chapter_outline": json.dumps(chapter_outline, ensure_ascii=False, indent=2),
            "target_words": target_words
        })
        
        current_length = len(initial_content)
        logger.info(f"初始内容生成完成，当前字数：{current_length}")
        logger.info(f"初始内容：\n{initial_content}")

        # 如果内容长度不足，使用expand_chain扩展
        if current_length < target_words:
            logger.info("内容长度不足，开始扩展...")
            expanded_content = self.expand_chain.invoke({
                "scenes": initial_content
            })
            current_length = len(expanded_content)
            logger.info(f"内容扩展完成，当前字数：{current_length}")
            logger.info(f"扩展内容：\n{expanded_content}")
            # 如果扩展后仍不足，使用enhance_chain优化
            if current_length < target_words:
                logger.info("内容仍需优化...")
                final_content = self.enhance_chain.invoke({
                    "content": expanded_content
                })
                logger.info(f"内容优化完成，最终字数：{len(final_content)}")
                logger.info(f"优化内容：\n{final_content}")
                return final_content
            return expanded_content
        
        return initial_content

import os

def main():
    # 记录开始时间
    start_time = datetime.now()
    logger.info(f"开始运行时间: {start_time}")
    
    generator = LongTextGenerator()
    topic = "龙傲天重生录"
    description = """故事题材为都市玄幻，大致讲述一个名叫龙傲天的主角重生在有超能力的都市，但他的超能力很弱，凭借着前世的智慧，一步步成为这个世界最强者的故事。可以分成5卷，每一卷都由多个章节组成，一个章节至少3000字，请开始书写第一章和第二章的内容。"""
    words = "3000"
    chapter_limit = 1  # Limit to first 2 chapters
    
    result = generator.generate_long_text(topic, description, words, chapter_limit)
    
    # Save result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "demo/novel_md"
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    output_file = os.path.join(output_dir, f"novel_{timestamp}.md")
    
    # 将结果保存到文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)
    
    # 记录结束时间和总用时
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"结束运行时间: {end_time}")
    logger.info(f"总用时: {duration}")
    logger.info(f"文章已保存到 {output_file}")


if __name__ == "__main__":
    main()

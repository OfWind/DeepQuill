from outline_generator import OutlineGenerator
from content_generator import ContentGenerator
from utils.file_handler import FileHandler
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取文件处理器
file_handler = FileHandler()

# 创建日志过滤器
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO

# 配置日志处理器
file_handler = logging.FileHandler(file_handler.get_log_path(), encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(InfoFilter())

# 配置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

class NovelGenerator:
    """小说生成器主类，整合大纲生成和内容生成功能"""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", base_dir: str = "demo"):
        """初始化小说生成器
        
        Args:
            model_name: 使用的模型名称
            base_dir: 基础目录
        """
        self.outline_generator = OutlineGenerator(model_name)
        self.content_generator = ContentGenerator(model_name, base_dir)
        self.file_handler = FileHandler(base_dir)
        logger.info("小说生成器初始化完成")
        
    def generate_chapter(self, topic: str, description: str, 
                        volume_number: int, chapter_number: int) -> Dict:
        """生成单个章节
        
        Args:
            topic: 小说主题
            description: 小说描述
            volume_number: 卷号
            chapter_number: 章节号
            
        Returns:
            Dict: 包含生成信息的字典
        """
        start_time = datetime.now()
        logger.info(f"开始生成第 {volume_number} 卷第 {chapter_number} 章")
        
        try:
            # 生成或加载大纲
            outline = self.outline_generator.generate_complete_outline(
                topic=topic,
                description=description,
                save=True
            )
            
            # 设置大纲
            self.content_generator.set_outline(outline)
            
            # 找到指定章节
            target_volume = None
            target_chapter = None
            
            for volume in outline["volumes"]:
                if volume["volume_number"] == volume_number:
                    target_volume = volume
                    for chapter in volume["chapters"]:
                        if chapter["chapter_number"] == chapter_number:
                            target_chapter = chapter
                            break
                    break
            
            if not target_volume or not target_chapter:
                raise ValueError(f"未找到第 {volume_number} 卷第 {chapter_number} 章")
            
            # 生成章节内容
            chapter_file = self.content_generator.generate_chapter_content(
                volume_number=volume_number,
                chapter=target_chapter
            )
            
            # 计算用时
            end_time = datetime.now()
            duration = end_time - start_time
            
            result = {
                "status": "success",
                "topic": topic,
                "volume_number": volume_number,
                "chapter_number": chapter_number,
                "chapter_title": target_chapter["chapter_title"],
                "chapter_file": chapter_file,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(duration)
            }
            
            logger.info(f"章节生成完成，用时: {duration}")
            return result
            
        except Exception as e:
            logger.error(f"生成章节时出错: {e}")
            raise
            
    def generate_from_outline(self, outline_path: str,
                            volume_number: int,
                            chapter_number: int) -> Dict:
        """从已有大纲生成章节内容
        
        Args:
            outline_path: 大纲文件路径
            volume_number: 卷号
            chapter_number: 章节号
            
        Returns:
            Dict: 包含生成信息的字典
        """
        start_time = datetime.now()
        logger.info(f"开始从大纲生成 {volume_number} 第 {chapter_number} 章")
        
        try:
            # 加载大纲
            self.content_generator.load_outline(outline_path)
            outline = self.content_generator.outline
            
            # 找到指定章节
            target_volume = None
            target_chapter = None
            
            for volume in outline["volumes"]:
                if volume["volume_number"] == volume_number:
                    target_volume = volume
                    for chapter in volume["chapters"]:
                        if chapter["chapter_number"] == chapter_number:
                            target_chapter = chapter
                            break
                    break
            
            if not target_volume or not target_chapter:
                raise ValueError(f"未找到第 {volume_number} 卷第 {chapter_number} 章")
            
            # 生成章节内容
            chapter_file = self.content_generator.generate_chapter_content(
                volume_number=volume_number,
                chapter=target_chapter
            )
            
            # 计算用时
            end_time = datetime.now()
            duration = end_time - start_time
            
            result = {
                "status": "success",
                "outline_file": outline_path,
                "volume_number": volume_number,
                "chapter_number": chapter_number,
                "chapter_title": target_chapter["chapter_title"],
                "chapter_file": chapter_file,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(duration)
            }
            
            logger.info(f"章节生成完成，用时: {duration}")
            return result
            
        except Exception as e:
            logger.error(f"从大纲生成章节时出错: {e}")
            raise

def main():
    """主函数，用于测试"""
    generator = NovelGenerator()
    
    # 测试参数
    topic = "龙傲天重生录"
    description = """故事题材为都市玄幻，大致讲述一个名叫龙傲天的主角重生在有超能力的都市，
    但他的超能力很弱，凭借着前世的智慧，一步步成为这个世界最强者的故事。"""
    
    # 生成第一卷第一章
    result = generator.generate_chapter(
        topic=topic,
        description=description,
        volume_number=1,
        chapter_number=1
    )
    
    logger.info(f"生成结果: {result}")

if __name__ == "__main__":
    main()

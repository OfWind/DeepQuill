import os
from datetime import datetime

class FileHandler:
    """文件处理工具类，统一管理文件路径和操作"""
    
    def __init__(self, base_dir: str = "demo"):
        """初始化文件处理器
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        self._init_dirs()
        
    def _init_dirs(self):
        """初始化所需的目录结构"""
        # 定义目录结构
        self.dirs = {
            "outlines": os.path.join(self.base_dir, "outlines"),
            "chapters": os.path.join(self.base_dir, "chapters"),
            "volumes": os.path.join(self.base_dir, "volumes"),
            "logs": os.path.join(self.base_dir, "logs")
        }
        
        # 创建目录
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
            
    def get_log_path(self) -> str:
        """获取日志文件路径"""
        return os.path.join(self.dirs["logs"], "novel.log")
        
    def get_outline_path(self, timestamp: str = None) -> str:
        """获取大纲文件路径
        
        Args:
            timestamp: 时间戳（可选）
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.dirs["outlines"], f"outline_{timestamp}.json")
        
    def get_chapter_path(self, volume_number: int, chapter_number: int) -> str:
        """获取章节文件路径
        
        Args:
            volume_number: 卷号
            chapter_number: 章节号
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chapter_{volume_number}_{chapter_number}_{timestamp}.md"
        return os.path.join(self.dirs["chapters"], filename)
        
    def get_volume_path(self, volume_number: int) -> str:
        """获取分卷文件路径
        
        Args:
            volume_number: 卷号
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"volume_{volume_number}_{timestamp}.md"
        return os.path.join(self.dirs["volumes"], filename)
        
    def merge_chapters(self, chapter_files: list, output_path: str) -> None:
        """合并多个章节文件
        
        Args:
            chapter_files: 章节文件路径列表
            output_path: 输出文件路径
        """
        merged_content = []
        for filepath in chapter_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                merged_content.append(f.read())
                merged_content.append("\n\n")
                
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("".join(merged_content)) 
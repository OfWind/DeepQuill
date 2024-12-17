import logging
import os
from utils.file_handler import FileHandler

class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO

def setup_logger(base_dir: str = "demo"):
    """配置统一的日志处理
    
    Args:
        base_dir: 基础目录
    """
    # 获取文件处理器
    file_handler = FileHandler(base_dir)
    
    # 配置日志处理器
    log_file = logging.FileHandler(file_handler.get_log_path(), encoding='utf-8')
    log_file.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(InfoFilter())
    
    # 配置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 添加处理器
    root_logger.addHandler(log_file)
    root_logger.addHandler(console_handler)
    
    return root_logger 
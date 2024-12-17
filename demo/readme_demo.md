# DeepQuill 小说生成器

## 项目说明
DeepQuill 是一个基于大语言模型的小说生成系统，能够自动生成小说大纲和内容。系统采用模块化设计，将大纲生成和内容生成分离，使得内容生成可以复用已有大纲，提高生成效率。

## 项目架构

### 核心模块
- `outline_generator.py`: 大纲生成模块
  - 书籍大纲生成：生成整本书的主题和分卷结构
  - 分卷大纲生成：生成每卷的章节结构
  - 章节大纲生成：生成每章的详细场景大纲
  - 大纲存储：将生成的大纲保存为JSON格式
  
- `content_generator.py`: 内容生成模块
  - 大纲加载：支持加载已有JSON格式大纲
  - 章节内容生成：基于大纲生成具体内容
  - 内容扩展：对生成内容进行扩展
  - 内容优化：优化文本质量和细节
  
- `novel_generator.py`: 主程序模块
  - 模块整合：协调大纲生成和内容生成
  - 进度控制：支持分章节生成和断点续写
  - 输出管理：统一管理文件输出格式

### 工具模块
- `prompts/`: 提示词模板目录
  - `outline_prompts.py`: 大纲生成��关提示词
  - `content_prompts.py`: 内容生成相关提示词
  
- `utils/`: 工具函数目录
  - `logger.py`: 日志配置
  - `file_handler.py`: 文件操作
  - `json_handler.py`: JSON处理

## 文件结构
```
demo/
├── main.py               # 主程序入口
├── outline_generator.py  # 大纲生成模块
├── content_generator.py  # 内容生成模块
├── prompts/             # 提示词模板
│   ├── outline_prompts.py
│   └── content_prompts.py
├── utils/               # 工具函数
│   ├── logger.py
│   ├── file_handler.py
│   └── json_handler.py
├── novel_md/             # 生成的小说文件
└── outlines/             # 保存的大纲文件
```

## 开发日志

### 2024-12-16
1. 项目初始化
   - 创建项目基础结构
   - 编写项目说明文档

2. 代码重构
   - 将原单文件结构拆分为多模块
   - 实现大纲生成和内容生成的解耦
   - 添加大纲保存和加载功能

### 2024-12-17
1. 架构优化
   - 创建main.py作为主程序入口
   - 优化content_generator.py，支持单章节生成
   - 完善文件路径管理
   - 将提示词模板移至独立文件

2. 功能增强
   - 添加单章节内容生成功能
   - 优化大纲加载和解析逻辑
   - 增强错误处理机制
   - 支持分离式大纲加载和内容生成

## 使用说明

### 生成新小说
```python
from main import NovelGenerator

generator = NovelGenerator()
generator.generate_novel(topic="小说主题", description="小说描述")
```

### 使用已有大纲生成内容
```python
from content_generator import ContentGenerator

# 生成单个章节
generator = ContentGenerator()
chapter_file = generator.generate_from_outlines(
    book_outline_path="outlines/book_outline.json",
    volume_outline_path="outlines/volume_outline.json",
    chapter_outline_path="outlines/chapter_outline.json",
    volume_number=1,
    chapter_number=1
)
print(f"章节内容已保存到: {chapter_file}")
```

## 注意事项
1. 使用前需要配置相应的API密钥
2. 建议先生成大纲并保存，再进行内容生成
3. 生成内容时需要提供完整的大纲文件
4. 单章节生成功能需要正确的大纲文件和章节编号
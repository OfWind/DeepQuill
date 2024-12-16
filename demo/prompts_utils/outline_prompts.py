from langchain_core.prompts import ChatPromptTemplate

# 书籍大纲生成提示词
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

# 分卷章节大纲生成提示词
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

# 章节详细大纲生成提示词
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
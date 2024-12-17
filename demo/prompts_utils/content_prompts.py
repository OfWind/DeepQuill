from langchain_core.prompts import ChatPromptTemplate

# 章节内容生成提示词
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
# 扩展章节内容的提示词
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

# 内容优化的提示词
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

# Novel Writing AI Agent

一个基于大语言模型的小说创作AI助手系统，能够帮助生成和管理长篇小说创作。

## 项目目标

开发一个能够辅助/自主创作生成连贯长篇小说的AI系统,实现:
- 故事情节的规划与推进
- 人物塑造与发展
- 场景描写生成
- 对话设计
- 文本风格把控
- 维护故事的连贯性和一致性

## 实现方案

### 记忆管理策略
1. 分层存储
   - 核心设定层：人物、世界观等基础设定（结构化存储）
   - 动态摘要层：章节摘要、人物发展记录
   - 工作记忆层：当前上下文、场景状态

2. 信息压缩策略
   - 智能摘要生成
   - 关键信息提取
   - 结构化数据存储

3. 上下文管理
   - 动态上下文组装
   - 智能信息筛选
   - 实时一致性检查

## 系统架构

### 核心模块
1. Story Planning Module (故事规划模块)
   - 情节设计与生成
   - 故事结构管理
   - 剧情推进控制
   - 章节管理

2. Character Management System (人物管理系统)
   - 人物档案管理
   - 人物关系图谱
   - 人物性格发展追踪
   - 对话生成系统

3. World Building Module (世界观构建模块)
   - 背景设定管理
   - 规则体系维护
   - 时间线管理
   - 场景描写生成

4. Memory Management System (记忆管理系统)
   - 上下文状态追踪
   - 情节连贯性维护
   - 设定一致性检查
   - 结构化信息存储

5. Text Generation Engine (文本生成引擎)
   - 场景描写生成
   - 对话生成
   - 情节展开描写

6. Quality Control System (质量控制系统)
   - 文本连贯性检查
   - 情节逻辑性验证
   - 人物行为合理性审查
   - 风格一致性控制

### 技术栈
- Python 3.10+
- LangChain、Langgraph、swarm
- Large Language Model (如 GPT、Claude、Gemini、LLaMA等)
- NetworkX (用于人物关系图谱)
- 其他待定...

## 项目结构
```
novel_agent/
├── src/
│   ├── core/
│   │   ├── agent.py          # 核心Agent类
│   │   ├── story_engine.py   # 故事生成引擎
│   │   └── memory_manager.py # 记忆管理系统
│   ├── characters/
│   │   ├── character.py      # 人物基类
│   │   └── character_system.py # 人物管理系统
│   ├── world/
│   │   └── world_builder.py  # 世界观构建系统
│   ├── memory/
│   │   ├── memory_store.py   # 记忆存储
│   │   └── memory_system.py  # 记忆管理
│   ├── quality/
│   │   └── quality_control.py # 质量控制系统
│   └── utils/
│       ├── config.py         # 配置管理
│       └── text_utils.py     # 文本处理工具
├── config/
│   └── story_config.yaml    # 故事配置文件
├── tests/
└── examples/
```

## 开发路线

### Phase 1 - MVP (当前阶段)
- [x] 项目框架设计
- [x] 确定核心架构和实现方案
- [ ] 核心Agent类实现
  - [ ] 基础框架搭建
  - [ ] LLM接口集成
  - [ ] 基础prompt模板
- [ ] 记忆管理系统
  - [ ] 核心设定存储
  - [ ] 上下文管理
  - [ ] 信息压缩机制
- [ ] 基础故事生成流程

### Phase 2 - 基础功能
- [ ] 人物系统实现
  - [ ] 人物属性管理
  - [ ] 关系图谱
  - [ ] 性格发展追踪
- [ ] 章节生成器开发
- [ ] 记忆管理系统完善
- [ ] 基础对话生成
- [ ] 质量控制基础功能

### Phase 3 - 增强功能
- [ ] 高级情节规划
- [ ] 多角色互动系统
- [ ] 写作风格定制
- [ ] 完整质量评估体系
- [ ] 性能优化

## 当前进度
- [x] 完成项目整体架构设计
- [x] 确定记忆管理策略
- [x] 开始实现核心Agent类
- [x] 实现Character基础类
  - [x] 基础属���管理
  - [x] 特征系统
  - [x] 关系系统
  - [x] 发展历史记录
- [x] 实现CharacterSystem类
  - [x] 角色管理功能
  - [x] 关系网络管理
  - [x] 互动历史记录
  - [x] 网络分析功能
- [ ] 下一步: 实现WorldBuilder类

## 最近更新
1. 实现了Character类的核心功能：
   - 使用dataclass实现了CharacterTrait和Relationship数据结构
   - 实现了特征(traits)的添加和修改功能
   - 实现了关系(relationships)的添加和修改功能
   - 添加了角色发展历史记录功能
   - 实现了角色信息的格式化输出

2. 实现了CharacterSystem类：
   - 使用NetworkX实现角色关系图谱
   - 支持角色间关系的双向管理
   - 记录角色间互动历史
   - 提供网络分析功能（中心性、群组等）
   - 支持角色发展的追踪和更新

3. 系统功能展示：
   - 成功演示了角色创建和属性管理
   - 展示了角色关系的建立和发展
   - 实现了互动影响机制
   - 提供了完整的系统状态摘要

## 下一步计划
1. 实现WorldBuilder类来管理世界观设定
2. 完善记忆管理系统
3. 开发故事生成引擎
4. 修复已知问题：
   - 网络分析的JSON序列化问题
   - 导入路径的优化
   - 添加更多的单元测试

## 贡献指南
待补充...

## 许可证
待定...

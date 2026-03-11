# Obsidian 私有化知识库 Agent

笔记越记越多，但找东西还是靠 Ctrl+F 搜关键词。
搜"神经网络"找不到写"深度学习"的笔记，知识沉淀了但用不起来。

所以做了这个东西，用自然语言直接问自己的笔记。

"我之前学过哪些 Python 相关的内容？"
"RAG 和传统搜索有什么区别？"

全程本地运行，笔记不上传任何云端。

## 技术栈

| 技术 | 作用 |
|---|---|
| LangChain | 整体框架 |
| Ollama | 本地运行AI模型 |
| nomic-embed-text | Embedding模型，文字转向量 |
| qwen2.5:1.5b | 本地LLM，生成回答 |
| Qdrant | 向量数据库 |
| Docker | 运行Qdrant容器 |

## 核心流程

笔记(.md) → 切块 → 向量化 → 存入Qdrant

提问 → 检索相关块 → 拼入Prompt → LLM生成回答

## 进度

- [x] 文档读取与切块
- [x] 本地Embedding向量化
- [x] Qdrant向量数据库存储
- [x] 语义检索
- [x] 本地LLM问答
- [x] FastAPI接口
- [x] Vue3前端界面
- [ ] Agent功能

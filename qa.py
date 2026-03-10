from langchain_ollama import OllamaEmbeddings, ChatOllama  # Embedding模型 + 对话模型
from langchain_qdrant import QdrantVectorStore              # Qdrant向量数据库封装
from qdrant_client import QdrantClient                      # Qdrant客户端
from langchain_core.prompts import PromptTemplate           # 提示词模板
from langchain_core.runnables import RunnablePassthrough    # 把输入直接传递下去
from langchain_core.output_parsers import StrOutputParser   # 把LLM输出转成字符串

# ---- 第一步：连接已有的Qdrant数据库 ----
client = QdrantClient(host="localhost", port=6333)

# ---- 第二步：初始化Embedding模型 ----
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"                                # 必须和ingest.py里一样
)

# ---- 第三步：连接已有的集合 ----
vector_store = QdrantVectorStore(
    client=client,
    collection_name="obsidian",
    embedding=embeddings
)

# ---- 第四步：初始化LLM ----
llm = ChatOllama(
    model="qwen2.5:1.5b",
    temperature=0                                           # 0表示回答更稳定不随机
)

# ---- 第五步：构建Prompt模板 ----
prompt = PromptTemplate.from_template("""你是一个知识库助手，根据以下资料回答问题。
如果资料中没有相关信息，就说不知道，不要编造答案。

资料：
{context}

问题：{question}
回答：""")

# ---- 第六步：构建检索链 ----
retriever = vector_store.as_retriever(search_kwargs={"k": 2})  # 检索最相关的2块

def format_docs(docs):
    # 把检索到的多个文档块拼成一段文字
    return "\n\n".join(doc.page_content for doc in docs)

# 用 | 把各步骤串联起来，这是LangChain新版本的写法，叫LCEL
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt                                                # 把context和question填入模板
    | llm                                                   # 发给LLM生成回答
    | StrOutputParser()                                     # 把LLM输出转成纯字符串
)

# ---- 第七步：提问 ----
question = "什么是RAG？"
answer = chain.invoke(question)

print(f"问题：{question}")
print(f"回答：{answer}")

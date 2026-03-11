from fastapi.middleware.cors import CORSMiddleware  # 导入跨域中间件
from fastapi import FastAPI          # 导入FastAPI类，用来创建服务器程序
from pydantic import BaseModel       # 导入BaseModel类，用来定义数据结构
from langchain_ollama import OllamaEmbeddings, ChatOllama  # Embedding模型和LLM
from langchain_qdrant import QdrantVectorStore              # Qdrant向量数据库封装
from qdrant_client import QdrantClient                      # Qdrant客户端
from langchain_core.prompts import PromptTemplate           # 提示词模板
from langchain_core.runnables import RunnablePassthrough    # 直接传递输入，不做处理
from langchain_core.output_parsers import StrOutputParser   # 把LLM输出转成纯字符串

# ---- 实例化FastAPI，创建服务器程序 ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允许所有来源的请求，* 表示通配符，即全部允许
    allow_methods=["*"],    # 允许所有 HTTP 请求方法，包括 GET、POST 等
    allow_headers=["*"],    # 允许所有请求头字段
)
# ---- 定义请求体的数据结构 ----
# BaseModel是pydantic库提供的类，继承它之后FastAPI能自动把JSON解析成这个类的实例
class AskRequest(BaseModel):
    question: str                    # 声明一个字段：问题，类型是字符串

# ---- 定义响应体的数据结构 ----
class AskResponse(BaseModel):
    answer: str                      # 声明一个字段：回答，类型是字符串

# ---- 初始化所有组件（程序启动时执行一次）----
client = QdrantClient(host="localhost", port=6333)  # 连接Qdrant数据库

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"         # Embedding模型，把文字变向量
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="obsidian",      # 连接已有的集合
    embedding=embeddings
)

llm = ChatOllama(
    model="qwen2.5:1.5b",
    temperature=0                    # 0表示回答更稳定，不随机
)

prompt = PromptTemplate.from_template("""你是一个知识库助手，根据以下资料回答问题。
如果资料中没有相关信息，就说不知道，不要编造答案。

资料：
{context}

问题：{question}
回答：""")

retriever = vector_store.as_retriever(search_kwargs={"k": 2})

def format_docs(docs):
    # 把检索到的多个文档块拼接成一段文字
    return "\n\n".join(doc.page_content for doc in docs)

# 用管道符把各步骤串联成一条链
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ---- 注册接口：POST /ask ----
# 装饰器把ask函数注册到app的路由表里，收到POST /ask请求时自动调用
@app.post("/ask")
def ask(request: AskRequest) -> AskResponse:
    # request.question 取出请求体里的question字段
    answer = chain.invoke(request.question)
    # 把答案包装成AskResponse对象返回，FastAPI自动转成JSON
    return AskResponse(answer=answer)

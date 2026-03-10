from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings          # 调用Ollama本地模型做向量化
from langchain_qdrant import QdrantVectorStore          # LangChain的Qdrant封装
from qdrant_client import QdrantClient                  # Qdrant客户端
from qdrant_client.models import Distance, VectorParams # 配置向量数据库参数用

# ---- 第一步：读取文件 ----
loader = TextLoader("docs/test.md")
documents = loader.load()

# ---- 第二步：切块 ----
splitter = CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)
chunks = splitter.split_documents(documents)
print(f"切块完成，共 {len(chunks)} 块")

# ---- 第三步：初始化Embedding模型 ----
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"        # 使用刚才pull下来的本地模型
)

# ---- 第四步：初始化Qdrant数据库 ----
client = QdrantClient(host="localhost", port=6333)  # 连接Docker里的Qdrant
client.create_collection(
    collection_name="obsidian",                      # 集合名，相当于数据库的表名
    vectors_config=VectorParams(
        size=768,                                    # nomic-embed-text向量维度是768
        distance=Distance.COSINE                     # 用余弦相似度计算向量距离
    )
)

# ---- 第五步：向量化并存入Qdrant ----
vector_store = QdrantVectorStore(
    client=client,
    collection_name="obsidian",
    embedding=embeddings                             # 告诉它用哪个Embedding模型
)
vector_store.add_documents(chunks)                   # 把所有chunk向量化后存进去
print("向量化完成，已存入Qdrant")

# ---- 第六步：测试检索 ----
query = "什么是RAG？"
results = vector_store.similarity_search(query, k=2) # 找最相似的2块

print(f"\n查询：{query}")
print("检索结果：")
for i, doc in enumerate(results):
    print(f"\n--- 第 {i+1} 个结果 ---")
    print(doc.page_content)

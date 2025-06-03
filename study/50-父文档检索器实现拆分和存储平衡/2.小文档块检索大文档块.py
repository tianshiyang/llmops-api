#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM3:01
@Author  : tianshiyang
@File    : 2.小文档块检索大文档块.py
"""
import dotenv
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
import weaviate
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

loaders = [
    UnstructuredLoader("电商产品数据.txt"),
    UnstructuredLoader("项目API文档.md")
]

docs = []
for loader in loaders:
    docs.extend(loader.load())

# 2.创建文本分割器
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

vector_store = WeaviateVectorStore(
    client=client,
    index_name="ParentDocument",
    text_key="text",
    embedding=DashScopeEmbeddings()
)

store = LocalFileStore("./parent-document")
retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
# 5.添加文档
retriever.add_documents(docs)

# 6.检索并返回内容
search_docs = retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))
client.close()

#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:24
@Author  : tianshiyang
@File    : 2.as_retriever检索器示例.py
"""
import dotenv
import weaviate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

documents = UnstructuredLoader('项目API文档.md').load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", "", ],
    is_separator_regex=True,
    add_start_index=True
)

chunks = text_splitter.split_documents(documents)

embedding = DashScopeEmbeddings()

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

db = WeaviateVectorStore(
    client=weaviate_client,
    embedding=embedding,
    index_name="DatasetDemo",
    text_key="text"
)

# db.add_documents(chunks)

retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
)

docs = retriever.invoke("关于配置接口的信息有哪些")

# print(list(document.page_content[:50] for document in docs))
# print(len(documents))
#

for doc in docs:
    print(doc.page_content, doc.metadata)

weaviate_client.close()

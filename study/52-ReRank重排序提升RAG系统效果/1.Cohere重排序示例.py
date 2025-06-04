#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.6.25 PM6:28
@Author  : tianshiyang
@File    : 1.Cohere重排序示例.py
"""
import os

import dotenv
from langchain.retrievers import ContextualCompressionRetriever
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings
from langchain_cohere import CohereRerank
import weaviate

dotenv.load_dotenv()

embedding = DashScopeEmbeddings()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

db = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    text_key="text",
    index_name="DatasetDemo",
)

rerank = CohereRerank(cohere_api_key=os.getenv("COHERE_API_KEY"), model="rerank-multilingual-v3.0")

retriever = ContextualCompressionRetriever(
    base_retriever=db.as_retriever(search_type="mmr"),
    base_compressor=rerank,
)

result = retriever.invoke("关于LLMOps应用配置的信息有哪些呢？")
client.close()
print(result)

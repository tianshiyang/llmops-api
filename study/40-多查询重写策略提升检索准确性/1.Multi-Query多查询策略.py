#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.5.25 PM10:22
@Author  : tianshiyang
@File    : 1.Multi-Query多查询策略.py
"""
import os

import dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
import weaviate
from langchain.retrievers import MultiQueryRetriever

from custom_embeddings import DashScopeEmbeddings

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

retriever = db.as_retriever(search_type="mmr")

llm = ChatOpenAI(
    model="moonshot-v1-8k",
    temperature=0,
)

# 2.创建多查询检索器
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm,
    include_original=True,
    prompt=PromptTemplate.from_template("""
        你是一个 AI 语言模型助手。你的任务是针对用户提出的问题，生成 3 个不同版本的问题，以便从向量数据库中检索相关文档。
        通过从多个角度改写用户的问题，你的目标是帮助用户克服基于距离的相似度检索所存在的一些局限性。
        请将这些改写后的问题用换行符分隔。
        原始问题：{question}
    """)
)

documents = multi_query_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(documents)

# 3.执行检索
client.close()

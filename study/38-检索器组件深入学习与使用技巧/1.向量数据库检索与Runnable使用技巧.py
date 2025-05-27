#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 25.5.25 PM11:26
@Author  : tianshiyang
@File    : 1.向量数据库检索与Runnable使用技巧.py
"""
import dotenv
import weaviate
from langchain_core.runnables import ConfigurableField
from langchain_weaviate import WeaviateVectorStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

embedding = DashScopeEmbeddings()

db = WeaviateVectorStore(
    client=client,
    embedding=embedding,
    index_name="DatasetDemo",
    text_key="text",
)

retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.5}
).configurable_fields(
    search_type=ConfigurableField(id="db_search_type"),
    search_kwargs=ConfigurableField(id="db_search_kwargs"),
)

mmr_documents = retriever.with_config(
    configurable={
        "db_search_type": "mmr",
        "db_search_kwargs": {
            "k": 4
        }
    }
).invoke("关于应用配置的接口有哪些？")

client.close()

print(len(mmr_documents))

for doc in mmr_documents:
    print(doc.page_content)

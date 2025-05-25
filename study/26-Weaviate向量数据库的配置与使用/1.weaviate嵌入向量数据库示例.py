#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 23.5.25 PM3:54
@Author  : tianshiyang
@File    : 1.weaviate嵌入向量数据库示例.py
"""
import weaviate
from langchain_weaviate import WeaviateVectorStore
from weaviate.classes.query import Filter

from custom_embeddings import DashScopeEmbeddings

# 1.原始文本数据与元数据
texts = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心。",
]
metadatas = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url="ngnmvr3ramond1aijic1q.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials="6Xp4tPGmAIj0AotqS3ZsIc2DMh3LC6Q4LjwY"
)

embedding = DashScopeEmbeddings()

db = WeaviateVectorStore(
    client=weaviate_client,
    index_name="Dataset",
    text_key="text",
    embedding=embedding,
)

# ids = db.add_texts(texts, metadatas)

# print(ids)
filters = Filter.by_property("page").greater_or_equal(5)
result = db.similarity_search_with_score("笨笨", filters=filters)
print(result)
print(db.as_retriever().invoke("笨笨"))

weaviate_client.close()

#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 22.5.25 AM10:26
@Author  : tianshiyang
@File    : CacheBackEmbedding使用实例.py
"""
from typing import List

import dotenv
import numpy as np
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    num1 = np.dot(vec1, vec2)
    return num1 / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


store = LocalFileStore("./cache/")

embeddings = DashScopeEmbeddings()

cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    store,
    namespace=embeddings.model,
    query_embedding_cache=True,
)

content = cached_embedder.embed_documents([
    "我是慕小课",
    "慕小课是我",
    "上善若水"
])

print(cosine_similarity(content[0], content[1]))
print(f"1，3相似度{cosine_similarity(content[0], content[2])}")

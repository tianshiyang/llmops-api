#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.5.25 PM8:55
@Author  : tianshiyang
@File    : 01.OpenAI嵌入模型示例.py
"""
from typing import List

import numpy as np

import dotenv

from custom_embeddings import DashScopeEmbeddings

dotenv.load_dotenv()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算传入两个向量的余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)


# 1.创建文本嵌入模型
embeddings = DashScopeEmbeddings()

# 2.嵌入文本
query_vector = embeddings.embed_query("我叫慕小课，喜欢打篮球")

print(query_vector)
print(len(query_vector))

# 3.嵌入文本列表、字符串列表
documents_vector = embeddings.embed_documents([
    "我叫慕小课，我喜欢打篮球",
    "这个喜欢打篮球的人叫慕小课",
    "求知若渴，虚心若愚"
])

print(documents_vector)
print(len(documents_vector))

# 4.计算余弦相似度
print("向量1和向量2的相似度:", cosine_similarity(documents_vector[0], documents_vector[1]))
print("向量1和向量3的相似度:", cosine_similarity(documents_vector[0], documents_vector[2]))

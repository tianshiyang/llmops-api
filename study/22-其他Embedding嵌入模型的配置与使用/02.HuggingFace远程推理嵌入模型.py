#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 22.5.25 PM9:11
@Author  : tianshiyang
@File    : 02.HuggingFace远程推理嵌入模型.py
"""
import dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings

dotenv.load_dotenv()

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L12-v2"
)

query_vector = embeddings.embed_query("你好，我是慕小课，我喜欢打篮球游泳")

print(query_vector)
print(len(query_vector))

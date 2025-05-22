#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 22.5.25 AM10:11
@Author  : tianshiyang
@File    : qian_wen_embeddings.py
"""
import os
from typing import List

import dotenv
from langchain_core.embeddings.embeddings import Embeddings
from dashscope import TextEmbedding

dotenv.load_dotenv()


class DashScopeEmbeddings(Embeddings):
    def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY"), model: str = "text-embedding-v1"):
        self.api_key = api_key
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = TextEmbedding.call(
            model=self.model,
            input=texts,
            api_key=self.api_key
        )
        return [item["embedding"] for item in response.output["embeddings"]]

    def embed_query(self, text: str) -> List[float]:
        response = TextEmbedding.call(
            model=self.model,
            input=text,
            api_key=self.api_key
        )
        return response.output["embeddings"][0]["embedding"]

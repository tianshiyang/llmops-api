#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 22.5.25 AM10:11
@Author  : tianshiyang
@File    : qian_wen_embeddings.py
"""
import os
from itertools import islice
from typing import List

import dotenv
from langchain_core.embeddings.embeddings import Embeddings
from dashscope import TextEmbedding

dotenv.load_dotenv()


class DashScopeEmbeddings(Embeddings):
    def __init__(self, api_key: str = os.getenv("ALI_API_KEY_EMBEDDING"), model: str = "text-embedding-v1"):
        self.api_key = api_key
        self.model = model

    def _chunk(self, iterable, size):
        """Yield successive chunks from iterable of max length `size`."""
        it = iter(iterable)
        while chunk := list(islice(it, size)):
            yield chunk

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        for batch in self._chunk(texts, 25):  # DashScope batch size limit
            try:
                response = TextEmbedding.call(
                    model=self.model,
                    input=batch,
                    api_key=self.api_key
                )
                if not response.output or "embeddings" not in response.output:
                    raise ValueError(f"DashScope returned unexpected response: {response}")
                all_embeddings.extend([item["embedding"] for item in response.output["embeddings"]])
            except Exception as e:
                raise RuntimeError(f"DashScope batch failed: {str(e)}")
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        try:
            response = TextEmbedding.call(
                model=self.model,
                input=text,
                api_key=self.api_key
            )
            if not response.output or "embeddings" not in response.output:
                raise ValueError(f"DashScope returned unexpected response: {response}")
            return response.output["embeddings"][0]["embedding"]
        except Exception as e:
            raise RuntimeError(f"Error calling DashScope embed_query: {str(e)}")

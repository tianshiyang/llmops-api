#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.7.25 AM12:01
@Author  : tianshiyang
@File    : embeddings_service.py
"""
import tiktoken
from injector import inject
from dataclasses import dataclass

from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore
from redis import Redis

from custom_embeddings import DashScopeEmbeddings


@inject
@dataclass
class EmbeddingsService:
    """文本嵌入服务"""
    _store = RedisStore
    _embeddings: DashScopeEmbeddings
    _cache_backed_embeddings: CacheBackedEmbeddings
    redis_client: Redis

    def __init__(self, redis: Redis):
        """构造函数，初始化文本嵌入模型客户端、存储器、缓存客户端"""
        self._store = RedisStore(client=redis)
        self._embeddings = DashScopeEmbeddings()
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,
            namespace="embeddings",
        )

    @classmethod
    def calculate_token_count(cls, query: str) -> int:
        """计算传入的文本token数量"""
        encoding = tiktoken.encoding_for_model("gpt-3.5")
        return len(encoding.encode(query))

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def embeddings(self) -> DashScopeEmbeddings:
        return self._embeddings

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings

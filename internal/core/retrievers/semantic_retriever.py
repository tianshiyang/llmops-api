#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.7.25 PM10:40
@Author  : tianshiyang
@File    : semantic_retriever.py
"""
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from uuid import UUID

from langchain_weaviate import WeaviateVectorStore
from pydantic import Field
from weaviate.collections.classes.filters import Filter


class SemanticRetriever(BaseRetriever):
    """相似性检索器/向量检索器"""
    dataset_ids: list[UUID]
    vector_store: WeaviateVectorStore
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        """根据传递的query执行相似性检索"""
        # 1. 提取最大搜索条件k，默认值为4
        k = self.search_kwargs.get("k", 4)
        # 2.执行相似性检索并获取得分信息
        search_result = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            **{
                "filters": Filter.all_of([
                    Filter.by_property("dataset_id").contains_any([str(dataset_id) for dataset_id in self.dataset_ids]),
                    Filter.by_property("document_enabled").equal(True),
                    Filter.by_property("segment_enabled").equal(True)
                ]),
                **{k: v for k, v in self.search_kwargs.items() if k != 'k'},
            },
        )

        if search_result is None or len(search_result) == 0:
            return []
        lc_documents, scores = zip(*search_result)

        for lc_document, score in zip(lc_documents, scores):
            lc_document.metadata["score"] = score

        return list(lc_documents)

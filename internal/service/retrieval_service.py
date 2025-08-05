#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.7.25 PM10:58
@Author  : tianshiyang
@File    : retrieval_service.py
"""
from injector import inject
from dataclasses import dataclass

from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document as LCDocument

from internal.entity.dataset_entity import RetrievalStrategy, RetrievalSource
from internal.exception import NotFoundException
from internal.model import Account
from internal.model.dataset import Dataset, DatasetQuery, Segment
from sqlalchemy import update
from internal.service.base_service import BaseService
from internal.service.jieba_service import JiebaService
from internal.service.vector_database_service import VectorDatabaseService
from pkg.sqlalchemy import SQLAlchemy
from uuid import UUID


@inject
@dataclass
class RetrievalService(BaseService):
    db: SQLAlchemy
    vector_database_service: VectorDatabaseService
    jieba_service: JiebaService

    def search_in_datasets(
            self,
            dataset_ids: list[UUID],
            query: str,
            retrieval_strategy: RetrievalStrategy.SEMANTIC,
            k: int = 4,
            score: float = 0,
            retrival_source: str = RetrievalSource.HIT_TESTING,
            account: Account = None
    ) -> list[LCDocument]:
        """根据传递的query+知识库列表执行检索，并返回检索的文档+得分数据（如果检索策略为全文检索，则得分为0）"""
        # 1.提取知识库列表并校验权限同时更新知识库id
        datasets = self.db.session.query(Dataset).filter(
            Dataset.id.in_(dataset_ids),
            Dataset.account_id == account.id,
        ).all()
        if datasets is None or len(datasets) == 0:
            raise NotFoundException("当前无知识库可执行检索")

        # 2.构建不同种类的检索器
        from internal.core.retrievers import SemanticRetriever, FullTextRetriever

        semantic_retriever = SemanticRetriever(
            dataset_ids=dataset_ids,
            vector_store=self.vector_database_service.vector_store,
            search_kwargs={
                "k": k,
                "score_threshold": score,
            }
        )
        full_text_retriever = FullTextRetriever(
            db=self.db,
            dataset_ids=dataset_ids,
            jieba_service=self.jieba_service,
            search_kwargs={
                "k": k
            }
        )
        hybrid_retriever = EnsembleRetriever(
            retrievers=[full_text_retriever, semantic_retriever],
            weights=[0.5, 0.5]
        )

        # 3. 根据不同的检索策略执行检索
        if retrieval_strategy == RetrievalStrategy.SEMANTIC:
            lc_documents = semantic_retriever.invoke(query)[:k]
        elif retrieval_strategy == RetrievalStrategy.FULL_TEXT:
            lc_documents = full_text_retriever.invoke(query)[:k]
        else:
            lc_documents = hybrid_retriever.invoke(query)[:k]

        # 4.添加知识库查询记录（只存储唯一记录，也就是一个知识库如果检索了多篇文档，也只存储一条）
        unique_dataset_ids = list(set(str(lc_document.metadata["dataset_id"]) for lc_document in lc_documents))

        for dataset_id in unique_dataset_ids:
            self.create(
                DatasetQuery,
                dataset_id=dataset_id,
                query=query,
                source=retrival_source,
                # todo:等待APP配置模块完成后进行调整
                source_app_id=None,
                created_by=account.id,
            )

        # 5.批量更新片段的命中次数，召回次数，涵盖了构建+执行语句
        with self.db.auto_commit():
            stmt = (
                update(Segment)
                .where(Segment.id.in_([lc_document.metadata["segment_id"] for lc_document in lc_documents]))
                .values(hit_count=Segment.hit_count + 1)
            )
            self.db.session.execute(stmt)
        return lc_documents

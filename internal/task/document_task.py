#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 4.7.25 PM2:10
@Author  : tianshiyang
@File    : document_task.py
"""
from uuid import UUID

from celery import shared_task


@shared_task
def build_documents(document_ids: list[UUID]) -> None:
    """根据传递的文档id列表，构建文档"""
    from internal.service.indexing_service import IndexingService
    from app.http.moudle import injector
    indexing_service = injector.get(IndexingService)
    indexing_service.build_documents(document_ids)


@shared_task
def update_document_enabled(document_id: UUID) -> None:
    """根据传递的文档id修改状态"""
    from app.http.moudle import injector
    from internal.service.indexing_service import IndexingService
    indexing_service = injector.get(IndexingService)
    indexing_service.update_document_enabled(document_id)


@shared_task
def delete_document(dataset_id: UUID, document_id: UUID) -> None:
    """根据传递的文档id+知识库id清除文档记录"""
    from app.http.moudle import injector
    from internal.service.indexing_service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_document(dataset_id, document_id)

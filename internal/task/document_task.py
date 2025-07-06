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
def build_documents(document_ids: list[UUID]):
    """根据传递的文档id列表，构建文档"""
    from internal.service.indexing_service import IndexingService
    from app.http.moudle import injector
    indexing_service = injector.get(IndexingService)
    indexing_service.build_documents(document_ids)

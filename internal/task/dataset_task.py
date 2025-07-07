#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 7.7.25 PM11:22
@Author  : tianshiyang
@File    : dataset_task.py
"""
from celery import shared_task
from uuid import UUID


@shared_task
def delete_dataset(dataset_id: UUID) -> None:
    """根据传递的知识库id删除特定的知识库信息"""
    from app.http.moudle import injector
    from internal.service.indexing_service import IndexingService
    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)

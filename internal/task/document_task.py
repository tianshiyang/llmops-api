#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 4.7.25 PM2:10
@Author  : tianshiyang
@File    : document_task.py
"""
from typing import List
from uuid import UUID

from celery import shared_task


@shared_task
def build_documents(document_ids: List[UUID]):
    """根据传递的文档id列表，构建文档"""
    pass

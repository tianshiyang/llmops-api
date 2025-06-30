#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 30.6.25 AM9:49
@Author  : tianshiyang
@File    : demo_task.py
"""
import logging
import time

from uuid import UUID
from celery import shared_task
from flask import current_app


@shared_task
def demo_task(id: UUID) -> str:
    """测试异步任务"""
    logging.error("睡眠5秒")
    time.sleep(5)
    logging.error(f"id的值:{id}")
    logging.error(f"配置信息:{current_app.config}")
    return "慕小课"

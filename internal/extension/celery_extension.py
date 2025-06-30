#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 29.6.25 PM10:41
@Author  : tianshiyang
@File    : celery_extension.py
"""
from celery import Celery, Task
from flask import Flask


def init_app(app: Flask):
    """Celery配置服务初始化"""

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()

    # 2.将celery挂在到app的扩展中
    app.extensions["celery"] = celery_app

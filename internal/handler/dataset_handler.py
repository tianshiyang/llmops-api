#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:12
@Author  : tianshiyang
@File    : dataset_handler.py
"""
from injector import inject
from dataclasses import dataclass

from internal.exception import ValidateErrorException
from internal.schema.dataset_schema import CreateDataSetReq
from internal.service.dataset_service import DatasetService
from pkg.response import success_message


@inject
@dataclass()
class DatasetHandler:
    # 知识库处理模块
    dataset_service: DatasetService

    def create_dataset(self):
        req = CreateDataSetReq()
        if not req.validate():
            raise ValidateErrorException(req.errors)

        # 创建知识库
        self.dataset_service.create_dataset(req)
        # 3.返回成功调用提示
        return success_message("创建知识库成功")

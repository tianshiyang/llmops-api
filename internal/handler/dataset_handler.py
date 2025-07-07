#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:12
@Author  : tianshiyang
@File    : dataset_handler.py
"""
import logging

from flask import request
from injector import inject
from dataclasses import dataclass

from wtforms.validators import UUID

from internal.exception import ValidateErrorException
from internal.schema.dataset_schema import CreateDataSetReq, GetDatasetWithPageReq, GetDatasetsWithPageResp, \
    GetDatasetResp, UpdateDatasetReq, GetDatasetQueriesResp
from internal.service.dataset_service import DatasetService
from pkg.paginator.paginator import PageModel
from pkg.response import success_message, success_json
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass()
class DatasetHandler:
    # 知识库处理模块
    dataset_service: DatasetService
    db: SQLAlchemy

    def create_dataset(self):
        # 创建知识库
        req = CreateDataSetReq()
        if not req.validate():
            raise ValidateErrorException(req.errors)

        # 创建知识库
        self.dataset_service.create_dataset(req)
        # 3.返回成功调用提示
        return success_message("创建知识库成功")

    def get_datasets_with_page(self):
        req = GetDatasetWithPageReq(request.args)
        if not req.validate():
            raise ValidateErrorException(req.errors)

        datasets, paginator = self.dataset_service.get_datasets_with_page(req)

        # 3.构建响应
        resp = GetDatasetsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(datasets), paginator=paginator))

    def get_dataset(self, dataset_id: UUID):
        # 获取知识库详情
        dataset = self.dataset_service.get_dataset(dataset_id)

        resp = GetDatasetResp()
        return success_json(resp.dump(dataset))

    def update_dataset(self, dataset_id: UUID):
        # 更新知识库详情
        req = UpdateDatasetReq()
        if not req.validate():
            raise ValidateErrorException(req.errors)

        self.dataset_service.update_dataset(dataset_id, req)

        # 3.返回成功调用提示
        return success_message("更新知识库成功")

    def get_dataset_queries(self, dataset_id: UUID):
        """根据传递的知识库id获取最近的10条查询记录"""
        dataset_queries = self.dataset_service.get_dataset_queries(dataset_id)
        resp = GetDatasetQueriesResp(many=True)
        return success_json(resp.dump(dataset_queries))

    def delete_dataset(self, dataset_id: UUID):
        """根据出传递的知识库id删除知识库"""
        self.dataset_service.delete_dataset(dataset_id)
        return success_message("删除知识库成功")

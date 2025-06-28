#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:19
@Author  : tianshiyang
@File    : dataset_service.py
"""
from typing import List
from uuid import UUID

from sqlalchemy import desc

from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidateErrorException, NotFoundException
from internal.extension.database_extension import db
from internal.model.dataset import Dataset
from internal.schema.dataset_schema import CreateDataSetReq, GetDatasetWithPageReq
from internal.service.base_service import BaseService
from injector import inject
from dataclasses import dataclass

from pkg.paginator.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class DatasetService(BaseService):
    db: SQLAlchemy

    def create_dataset(self, req: CreateDataSetReq) -> Dataset:
        # 创建知识库
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        dataset = db.session.query(Dataset).filter_by(
            account_id=account_id,
            name=req.name.data,
        ).one_or_none()
        if dataset:
            raise ValidateErrorException(f"该知识库{req.name.data}已存在")
        # 2.检测是否传递了描述信息，如果没有传递需要补充上
        if not req.description.name:
            req.description.name = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        return self.create(
            Dataset,
            account_id=account_id,
            name=req.name.data,
            icon=req.icon.data,
            description=req.description.name,
        )

    def get_datasets_with_page(self, req: GetDatasetWithPageReq) -> tuple[List[Dataset], Paginator]:
        """根据传递的信息获取知识库列表分页数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 构建分页器查询器
        paginator = Paginator(db=self.db, req=req)
        # 构建筛选器
        filters = [Dataset.account_id == account_id]

        if req.search_word.data:
            filters.append(Dataset.name.ilike(f"%{req.search_word.data}%"))
        # 执行分页器查询结果
        datasets = paginator.paginate(
            self.db.session.query(Dataset).filter(*filters).order_by(desc("created_at"))
        )
        return datasets, paginator

    def get_dataset(self, dataset_id: UUID) -> Dataset:
        """根据传递的信息获取知识库列表分页数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"

        dataset = self.get(Dataset, dataset_id)
        print(dataset, '-----')
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")
        return dataset

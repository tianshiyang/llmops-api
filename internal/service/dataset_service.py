#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM11:19
@Author  : tianshiyang
@File    : dataset_service.py
"""
import logging
from typing import List
from uuid import UUID

from sqlalchemy import desc

from internal.entity.dataset_entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidateErrorException, NotFoundException, FailException
from internal.extension.database_extension import db
from internal.model.app import AppDatasetJoin
from internal.model.dataset import Dataset, DatasetQuery
from internal.schema.dataset_schema import CreateDataSetReq, GetDatasetWithPageReq, UpdateDatasetReq
from internal.service.base_service import BaseService
from injector import inject
from dataclasses import dataclass
from internal.task.dataset_task import delete_dataset

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
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")
        return dataset

    def update_dataset(self, dataset_id: UUID, req: UpdateDatasetReq):
        """根据传递的信息获取知识库列表分页数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        dataset = self.get(Dataset, dataset_id)
        if str(dataset.account_id) != account_id or dataset is None:
            raise NotFoundException("知识库不存在")

        # 校验名称是否重名
        check_dataset = self.db.session.query(Dataset).filter(
            Dataset.name == req.name.data,
            Dataset.account_id == account_id,
            Dataset.id != dataset_id
        ).one_or_none()

        if check_dataset:
            raise ValidateErrorException(f"该知识库名称{req.name.data}已存在，请修改")

        # 3.校验描述信息是否为空，如果为空则人为设置
        if req.description.data is None or req.description.data.strip() == "":
            req.description.data = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(name=req.name.data)

        self.update(dataset, name=req.name.data, icon=req.icon.data, description=req.description.data)
        return dataset

    def get_dataset_queries(self, dataset_id: UUID) -> list[DatasetQuery]:
        """根据传递的知识库id获取最近的10条查询记录"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1.获取知识库并校验权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        # 2.调用知识库查询模型查找最近的10条记录
        dataset_queries = self.db.session.query(DatasetQuery).filter(
            DatasetQuery.dataset_id == dataset_id,
        ).order_by(desc("created_at")).limit(10).all()

        return dataset_queries

    def delete_dataset(self, dataset_id: UUID):
        """根据传递的知识库id删除知识库信息，涵盖知识库底下的所有文档、片段、关键词，以及向量数据库里存储的数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在")

        try:
            # 删除知识库基础记录以及知识库和应用关联的记录
            self.delete(dataset)
            with self.db.auto_commit():
                self.db.session.query(AppDatasetJoin).filter(
                    AppDatasetJoin.dataset_id == dataset_id,
                ).delete()

            # 调用异步任务执行后续操作
            delete_dataset.delay(dataset_id)
        except Exception as e:
            logging.exception(f"删除知识库失败, dataset_id: {dataset_id}, 错误信息: {str(e)}")
            raise FailException(f"删除知识库失败，请稍后重试{e}")

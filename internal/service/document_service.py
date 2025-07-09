#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 3.7.25 PM11:56
@Author  : tianshiyang
@File    : document_service.py
"""
import logging
import random
import time

from injector import inject
from dataclasses import dataclass
from uuid import UUID

from redis import Redis
from sqlalchemy import desc

from internal.entity.cache_entity import LOCK_DOCUMENT_UPDATE_ENABLED, LOCK_EXPIRE_TIME
from internal.entity.dataset_entity import ProcessType, DocumentStatus
from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION
from internal.exception import ForbiddenException, FailException, NotFoundException
from internal.model.dataset import Document, Dataset, ProcessRule
from internal.model.upload_file import UploadFile
from internal.schema.dataset_schema import GetDatasetWithPageReq
from internal.service.base_service import BaseService
from pkg.paginator.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from internal.task.document_task import build_documents, update_document_enabled
from datetime import datetime


@inject
@dataclass
class DocumentService(BaseService):
    """文档服务"""
    db: SQLAlchemy
    redis_client: Redis

    def create_documents(
            self,
            dataset_id: UUID,
            upload_file_ids: list[UUID],
            process_type: str = ProcessType.AUTOMATIC,
            rule: dict = None
    ) -> tuple[list[Document], str]:
        """根据传递的信息创建文档列表并调用异步任务"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1. 检验知识库权限
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise ForbiddenException("当前用户无知识库权限或知识库不存在")
        # 2.提取文件并校验权限与文档扩展
        upload_files = self.db.session.query(UploadFile).filter(
            UploadFile.account_id == account_id,
            UploadFile.id.in_(upload_file_ids),
        ).all()

        upload_files = [
            upload_file for upload_file in upload_files
            if upload_file.extension.lower() in ALLOWED_DOCUMENT_EXTENSION
        ]

        if len(upload_files) == 0:
            logging.warning(
                f"上传文档列表未解析到合法文件，account_id:{account_id}, dataset_id:{dataset_id}, upload_file_id:{upload_file_ids}")
            raise FailException("暂未解析到合法文件，请重新上传")

        # 3. 创建批次与处理规则并记录到数据库中
        batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
        process_rule = self.create(
            ProcessRule,
            account_id=account_id,
            dataset_id=dataset_id,
            mode=process_type,
            rule=rule
        )

        # 4. 获取当前知识库的最新文档位置
        position = self.get_latest_document_position(dataset_id)

        # 5. 循环遍历所有合法的上传文件列表并记录
        documents = []
        for upload_file in upload_files:
            position = position + 1
            document = self.create(
                Document,
                dataset_id=dataset_id,
                account_id=account_id,
                upload_file_id=upload_file.id,
                process_rule_id=process_rule.id,
                batch=batch,
                position=position,
                name=upload_file.name,
            )
            documents.append(document)

        # 6. 调用异步任务完成后续操作
        build_documents.delay([document.id for document in documents])
        # 7. 返回文档列表和处理批次
        return documents, batch

    def get_latest_document_position(self, dataset_id: UUID) -> int:
        """根据传递的知识库id获取最新文档位置"""
        document = self.db.session.query(Document).filter(Document.dataset_id == dataset_id).order_by(
            desc("position")).first()
        return document.position if document else 0

    def get_documents_with_page(self, dataset_id: UUID, req: GetDatasetWithPageReq) -> tuple[list[Document], Paginator]:
        """根据传递的知识库id+请求数据获取文档分页列表数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        dataset = self.get(Dataset, dataset_id)
        if dataset is None or str(dataset.account_id) != account_id:
            raise NotFoundException("该知识库不存在，或无权限")

        # 2.构建分页查询器
        paginator = Paginator(db=self.db, req=req)

        # 3. 构建筛选器
        filters = [
            Document.dataset_id == dataset_id,
            Document.account_id == account_id
        ]
        if req.search_word.data:
            filters.append(Document.name.ilike(f"%{req.search_word.data}%"))

        # 4.执行分页并获取数据
        documents = paginator.paginate(
            self.db.session.query(Document).filter(*filters).order_by(desc("created_at"))
        )
        return documents, paginator

    def get_document(self, dataset_id: UUID, document_id: UUID) -> Document:
        """根据传递的知识库id+文档id获取文档记录信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise ForbiddenException("当前用户获取该文档，请核实后重试")
        return document

    def update_document(self, dataset_id: UUID, document_id: UUID, **kwargs) -> Document:
        """根据传递的知识库id+文档id，更新文档信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise ForbiddenException("当前用户无权限修改该文档，请核实后重试")
        return self.update(document, **kwargs)

    def update_document_enabled(self, dataset_id: UUID, document_id: UUID, enabled: bool) -> Document:
        """根据传递的知识库id+文档id，更新文档的启用状态，同时会异步更新weaviate向量数据库中的数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1. 获取文档并校验权限
        document = self.get(Document, document_id)
        if document is None:
            raise NotFoundException("该文档不存在，请核实后重试")
        if document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise ForbiddenException("当前用户无修改权限，请核实后重试")

        # 2.判断文档是否处于可修改状态，只有构建完成才可以修改enabled
        if document.status != DocumentStatus.COMPLETED:
            raise FailException(f"当前文档处于不可修改状态，请稍后重试")

        # 3.判断修改的启用状态时候正确，需要与当前状态相反
        if document.enabled == enabled:
            raise FailException(f"文档状态修改错误，当前已是{'启用' if enabled else '禁用'}状态")

        # 4. 获取更新文档启用状态的缓存键并检测是否上锁
        cache_key = LOCK_DOCUMENT_UPDATE_ENABLED.format(document_id=document.id)
        cache_result = self.redis_client.get(cache_key)
        if cache_result is not None:
            raise FailException("当前文档正在修改启用状态，请稍后再次尝试")

        # 5.修改文档的启用状态并设置缓存键，缓存时间为600s
        self.update(document, enabled=enabled, disabled_at=None if enabled else datetime.now())
        self.redis_client.setex(cache_key, LOCK_EXPIRE_TIME, 1)

        # 6.启用异步任务完成后续操作
        update_document_enabled.delay(document.id)
        return document

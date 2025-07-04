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

from sqlalchemy import desc

from internal.entity.dataset_entity import ProcessType
from internal.entity.upload_file_entity import ALLOWED_DOCUMENT_EXTENSION
from internal.exception import ForbiddenException, FailException
from internal.model.dataset import Document, Dataset, ProcessRule
from internal.model.upload_file import UploadFile
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.task.document_task import build_documents


@inject
@dataclass
class DocumentService(BaseService):
    """文档服务"""
    db: SQLAlchemy

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
            UploadFile.dataset_id == dataset_id,
            UploadFile.id.in_(upload_file_ids)
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

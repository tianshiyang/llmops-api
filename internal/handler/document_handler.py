#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2.7.25 PM11:46
@Author  : tianshiyang
@File    : document_handler.py
"""
from dataclasses import dataclass
from injector import inject
from uuid import UUID

from internal.schema.document_schema import CreateDocumentReq
from pkg.response import validate_error_json


@inject
@dataclass
class DocumentHandler:
    """知识库新增、上传文档列表"""
    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        req = CreateDocumentReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 调用服务并创建文档，返回文档列表信息+处理批次
        documents, batch = self.document_service.create_documents(dataset_id, *req.data)

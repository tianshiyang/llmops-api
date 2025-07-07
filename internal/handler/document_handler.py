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

from internal.schema.document_schema import CreateDocumentReq, CreateDocumentResp, GetDocumentWithPageReq, \
    GetDocumentsWithPageResp, GetDocumentResp
from internal.service.document_service import DocumentService
from pkg.paginator.paginator import PageModel
from pkg.response import validate_error_json, success_json
from flask import request


@inject
@dataclass
class DocumentHandler:
    """知识库新增、上传文档列表"""
    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        # 创建文档
        req = CreateDocumentReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 调用服务并创建文档，返回文档列表信息+处理批次
        documents, batch = self.document_service.create_documents(dataset_id, **req.data)
        # 3. 生成响应结构并返回
        resp = CreateDocumentResp()
        return success_json(resp.dump((documents, batch)))

    def get_documents_with_page(self, dataset_id: UUID):
        """根据传递的知识库id获取文档分页列表数据"""
        print(request.args, '-a--a-aa-')
        req = GetDocumentWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        documents, paginator = self.document_service.get_documents_with_page(dataset_id, req)
        # 构建响应结构并映射
        resp = GetDocumentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(documents), paginator=paginator))

    def get_document(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id获取文档详情信息"""
        document = self.document_service.get_document(dataset_id, document_id)
        resp = GetDocumentResp()
        return success_json(resp.dump(document))

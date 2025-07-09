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
    GetDocumentsWithPageResp, GetDocumentResp, UpdateDocumentNameReq, UpdateDocumentEnabledReq
from internal.service.document_service import DocumentService
from pkg.paginator.paginator import PageModel
from pkg.response import validate_error_json, success_json, success_message
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

    def update_document_name(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id更新对应文档的名称信息"""
        req = UpdateDocumentNameReq()
        if not req.validate():
            return validate_error_json(req.errors)
        # 调用服务更新文档的名称信息
        self.document_service.update_document(dataset_id, document_id, name=req.name.data)
        return success_message("更新文档名称成功")

    def update_document_enabled(self, dataset_id: UUID, document_id: UUID):
        """根据传递的知识库id+文档id更新指定文档的启用状态"""
        # 1.提取请求并校验
        req = UpdateDocumentEnabledReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.document_service.update_document_enabled(dataset_id, document_id, enabled=req.enabled.data)
        return success_message("更改文档启用状态成功")

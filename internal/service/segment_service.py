#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.7.25 PM4:55
@Author  : tianshiyang
@File    : segment_service.py
"""
from injector import inject
from dataclasses import dataclass

from sqlalchemy import asc

from internal.exception import ForbiddenException
from internal.model.dataset import Segment, Document
from internal.schema.segment_schema import GetSegmentsWithPageReq
from internal.service.base_service import BaseService
from pkg.paginator.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class SegmentService(BaseService):
    db: SQLAlchemy

    def get_segments_with_page(self, dataset_id, document_id, req: GetSegmentsWithPageReq) -> tuple[
        list[Segment], Paginator]:
        """根据传递的信息获取片段列表分页数据"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1.获取文档并校验权限
        document = self.get(Document, document_id)
        if document is None or document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise ForbiddenException("该知识库文档不存在，或无权限查看，请核实后重试")
        # 2.构建分页查询器
        paginator = Paginator(self.db, req=req)
        # 3.构建筛选器
        filters = [Segment.document_id == document_id]
        if req.search_word.data:
            filters.append(Segment.content.ilike(f"%{req.search_word.data}%"))

        # 4.执行分页并获取数据
        segments = paginator.paginate(
            self.db.session.query(Segment).filter(*filters).order_by(asc("position"))
        )
        return segments, paginator

#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.7.25 PM4:48
@Author  : tianshiyang
@File    : segment_handler.py
"""
from uuid import UUID

from injector import inject
from dataclasses import dataclass

from internal.schema.segment_schema import GetSegmentsWithPageReq, GetSegmentsWithPageResp
from internal.service.segment_service import SegmentService
from pkg.paginator.paginator import PageModel
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class SegmentHandler:
    segment_service: SegmentService

    def get_segments_with_page(self, dataset_id: UUID, document_id: UUID):
        """获取指定知识库文档的片段列表信息"""
        req = GetSegmentsWithPageReq()
        if not req.validate():
            return validate_error_json(req.errors)
        segments, paginator = self.segment_service.get_segments_with_page(dataset_id, document_id, req)
        resp = GetSegmentsWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(segments), paginator=paginator))

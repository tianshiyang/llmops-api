#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 5.7.25 PM1:01
@Author  : tianshiyang
@File    : keyword_table_service.py
"""
from injector import inject
from dataclasses import dataclass
from uuid import UUID
from internal.service.base_service import BaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.model.dataset import KeywordTable


@inject
@dataclass
class KeywordTableService(BaseService):
    """知识库关键词表服务"""
    db: SQLAlchemy

    def get_keyword_table_from_dataset_id(self, dataset_id: UUID) -> KeywordTable:
        """根据传递的知识库id获取关键词表"""
        keyword_table = self.db.session.query(KeywordTable).filter(
            KeywordTable.dataset_id == dataset_id,
        ).one_or_none()

        if keyword_table is None:
            keyword_table = self.create(KeywordTable, dataset_id=dataset_id, keyword_table={})

        return keyword_table

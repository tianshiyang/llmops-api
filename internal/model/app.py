#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 17:06
@Author  : 1685821150@qq.com
@File    : app.py
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, String, PrimaryKeyConstraint, Index, DateTime

from internal.extension.database_extension import db


class App(db.Model):
    """AI应用基础模型类"""
    __tablename__ = 'app'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='app_id_pk'),
        Index("idx_app_account_id", "account_id"),
    )

    id = Column(UUID, default=uuid.uuid4, nullable=False)
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), default="", nullable=False)
    icon = Column(String(255), default="", nullable=False)
    description = Column(String(255), default="", nullable=False)
    status = Column(String(255), default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

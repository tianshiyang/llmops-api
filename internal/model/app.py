#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/4/20 17:06
@Author  : 1685821150@qq.com
@File    : app.py
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, String, PrimaryKeyConstraint, Index, DateTime, text, Text

from internal.extension.database_extension import db


class App(db.Model):
    __tablename__ = 'app'
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id")
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # icon = Column(String(255), nullable=False, server_default=text("''::character varying"))
    description = Column(Text, nullable=False, server_default=text("''::text"))
    status = Column(String(255), nullable=False, server_default=text("''::character varying"))
    update_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    create_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))

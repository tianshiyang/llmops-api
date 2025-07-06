#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 28.6.25 PM10:51
@Author  : tianshiyang
@File    : dataset.py
"""
from sqlalchemy import PrimaryKeyConstraint, UUID, Column, text, Text, String, DateTime, Integer, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.functions import count

from internal.extension.database_extension import db
from internal.model.app import AppDatasetJoin
from internal.model.upload_file import UploadFile


class Dataset(db.Model):
    """知识库表"""
    __tablename__ = "dataset"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    icon = Column(String(255), nullable=False, server_default=text("''::character varying"))
    description = Column(Text, nullable=False, server_default=text("''::text"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def document_count(self) -> int:
        """只读属性，获取知识库下的文档数"""
        return (
            db.session.
            query(func.count(Document.id)).
            filter(Document.dataset_id == self.id).
            scalar()
        )

    @property
    def hit_count(self) -> int:
        """只读属性，获取该知识库的命中次数"""
        return (
            db.session.
            query(func.coalesce(func.sum(Segment.hit_count), 0)).
            filter(Segment.dataset_id == self.id).
            scalar()
        )

    @property
    def related_app_count(self) -> int:
        """只读属性，获取该知识库关联的应用数"""
        return (
            db.session.
            query(func.count(AppDatasetJoin.id)).
            filter(AppDatasetJoin.dataset_id == self.id).
            scalar()
        )

    @property
    def character_count(self) -> int:
        """只读属性，获取该知识库下的字符总数"""
        return (
            db.session.
            query(func.coalesce(func.sum(Document.character_count), 0)).
            filter(Document.dataset_id == self.id).
            scalar()
        )


class Document(db.Model):
    """文档表模型"""
    __tablename__ = "document"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_document_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    # 关联的知识库id
    dataset_id = Column(UUID, nullable=False)
    # 关联的文件id
    upload_file_id = Column(UUID, nullable=False)
    # 处理规则
    process_rule_id = Column(UUID, nullable=False)
    # 文档处理批次
    batch = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 文档名字
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 文档位置
    position = Column(Integer, nullable=False, server_default=text("1"))
    # 文档总字符数
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    # 文档token总数
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 开始处理时间
    processing_started_at = Column(DateTime, nullable=True)
    # 解析结束时间
    parsing_completed_at = Column(DateTime, nullable=True)
    # 分割结束时间
    splitting_completed_at = Column(DateTime, nullable=True)
    # 索引结束时间
    indexing_completed_at = Column(DateTime, nullable=True)
    # 构建完成时间
    completed_at = Column(DateTime, nullable=True)
    # 结束时间
    stopped_at = Column(DateTime, nullable=True)
    # 错误日志
    error = Column(Text, nullable=False, server_default=text("''::text"))
    # 是否启用
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    # 人为禁用时间
    disabled_at = Column(DateTime, nullable=True)
    # 状态
    status = Column(String(255), nullable=False, server_default=text("'waiting'::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

    @property
    def upload_file(self) -> "UploadFile":
        return db.session.query(UploadFile).filter(
            UploadFile.id == self.upload_file_id
        ).one_or_none()

    @property
    def process_rule(self) -> "ProcessRule":
        return db.session.query(ProcessRule).filter(
            ProcessRule.id == self.process_rule_id
        ).one_or_none()

    @property
    def segment_count(self):
        return db.session.query(func(count(Segment.id))).filter(
            Segment.document_id == self.id
        ).scalar()

    @property
    def hit_count(self) -> int:
        """命中次数"""
        return db.session.query(func.coalesce(func.sum(Segment.hit_count), 0)).filter(
            Segment.document_id == self.id,
        ).scalar()


class Segment(db.Model):
    """片段表模型"""
    __tablename__ = "segment"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_segment_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    # 关联知识库id
    dataset_id = Column(UUID, nullable=False)
    # 关联文档id
    document_id = Column(UUID, nullable=False)
    # 向量数据库节点id，用于快速查找
    node_id = Column(UUID, nullable=False)
    # 片段在文档的位置
    position = Column(Integer, nullable=False, server_default=text("1"))
    # 片段内容
    content = Column(Text, nullable=False, server_default=text("''::text"))
    # 片段长度
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    # token词数
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    # 关键词列表
    keywords = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    # 内容hash值
    hash = Column(String(255), nullable=False, server_default=text("''::character varying"))
    # 命中次数
    hit_count = Column(Integer, nullable=False, server_default=text("0"))
    # 是否启用
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    # 禁用时间
    disabled_at = Column(DateTime, nullable=True)
    # 开始处理时间
    processing_started_at = Column(DateTime, nullable=True)
    # 索引结束时间
    indexing_completed_at = Column(DateTime, nullable=True)
    # 构建完成时间戳
    completed_at = Column(DateTime, nullable=True)
    # 停止时间
    stopped_at = Column(DateTime, nullable=True)
    # 错误日志
    error = Column(Text, nullable=False, server_default=text("''::text"))
    # 状态2
    status = Column(String(255), nullable=False, server_default=text("'waiting'::character varying"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))


class KeywordTable(db.Model):
    """关键词表模型"""
    __tablename__ = "keyword_table"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_keyword_table_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    dataset_id = Column(UUID, nullable=False)
    keyword_table = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))


class DatasetQuery(db.Model):
    """知识库查询表模型"""
    __tablename__ = "dataset_query"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_query_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    dataset_id = Column(UUID, nullable=False)
    # 查询的query语句
    query = Column(Text, nullable=False, server_default=text("''::text"))
    # 查询的来源
    source = Column(String(255), nullable=False, server_default=text("'HitTesting'::character varying"))
    # 查询关联的应用id
    source_app_id = Column(UUID, nullable=True)
    # 创建查询的账号id
    created_by = Column(UUID, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))


class ProcessRule(db.Model):
    """文档处理规则表模型"""
    __tablename__ = "process_rule"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_process_rule_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    # 归属知识库id
    dataset_id = Column(UUID, nullable=False)
    # 处理模式
    mode = Column(String(255), nullable=False, server_default=text("'automic'::character varying"))
    # 处理规则
    rule = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

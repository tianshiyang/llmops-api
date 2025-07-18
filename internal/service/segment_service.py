#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 11.7.25 PM4:55
@Author  : tianshiyang
@File    : segment_service.py
"""
import logging
import uuid
from uuid import UUID

from injector import inject
from dataclasses import dataclass

from redis import Redis
from sqlalchemy import asc, func
from .keyword_table_service import KeywordTableService

from internal.entity.dataset_entity import DocumentStatus, SegmentStatus
from internal.exception import ForbiddenException, ValidateErrorException, NotFoundException, FailException
from internal.lib.helper import generate_text_hash
from internal.model.dataset import Segment, Document
from internal.schema.segment_schema import GetSegmentsWithPageReq, CreateSegmentReq, UpdateSegmentReq
from internal.service.base_service import BaseService
from internal.service.embeddings_service import EmbeddingsService
from internal.service.jieba_service import JiebaService
from internal.service.vector_database_service import VectorDatabaseService
from pkg.paginator.paginator import Paginator
from pkg.sqlalchemy import SQLAlchemy
from langchain_core.documents import Document as LCDocument
from datetime import datetime

from ..entity.cache_entity import LOCK_SEGMENT_UPDATE_ENABLED, LOCK_EXPIRE_TIME


@inject
@dataclass
class SegmentService(BaseService):
    db: SQLAlchemy
    vector_database_service: VectorDatabaseService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    keyword_table_service: KeywordTableService
    redis_client: Redis

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

    def create_segment(self, dataset_id: UUID, document_id: UUID, req: CreateSegmentReq) -> Segment:
        """根据传递的信息新增文档片段信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"

        # 1. 校验上传内容的token总长度数，不能超过1000
        token_count = self.embeddings_service.calculate_token_count(req.content.data)
        if token_count > 1000:
            raise ValidateErrorException("片段内容长度不能超过1000token")
        # 2.获取文档信息并校验
        document = self.get(Document, document_id)
        if document is None or document.dataset_id != dataset_id or str(document.account_id) != account_id:
            raise NotFoundException("该知识库不存在，或无权限，请核实后重试")
        # 3.判断文档的状态是否可以新增片段数据，只有complete可以新增
        if document.status != DocumentStatus.COMPLETED:
            raise FailException("当前文档不可新增片段，请稍后尝试")
        # 4.提取文档片段的最大位置
        position = self.db.session.query(func.coalesce(func.max(Segment.position), 0)).filter(
            Segment.document_id == document_id
        ).scalar()
        # 5.检测是否传递了keywords，如果没有传递的话，调用jieba服务生成关键词
        if req.keywords.data is None or len(req.keywords.data) == 0:
            req.keywords.data = self.jieba_service.extract_keywords(req.content.data, 10)
        # 6. 往postgres数据库中新增数据
        segment = None
        try:
            position += 1
            # 7.位置+1并新增segment记录
            segment = self.create(
                Segment,
                account_id=account_id,
                dataset_id=dataset_id,
                document_id=document_id,
                node_id=uuid.uuid4(),
                position=position,
                character_count=len(req.content.data),
                token_count=token_count,
                keywords=req.keywords.data,
                content=req.content.data,
                hash=generate_text_hash(req.content.data),
                enabled=True,
                processing_started_at=datetime.now(),
                indexing_completed_at=datetime.now(),
                completed_at=datetime.now(),
                status=SegmentStatus.COMPLETED
            )
            # 8.往向量数据库中新增数据
            self.vector_database_service.vector_store.add_documents(
                [LCDocument(
                    page_content=req.content.data,
                    metadata={
                        "account_id": account_id,
                        "dataset_id": str(document.dataset_id),
                        "document_id": str(document.id),
                        "segment_id": str(segment.id),
                        "node_id": str(segment.node_id),
                        "document_enabled": document.enabled,
                        "segment_enabled": True,
                    }
                )],
                ids=[str(segment.node_id)]
            )
            # 9.重新计算片段的字符总数以及token总数
            document_character_count, document_token_count = self.db.session.query(
                func.coalesce(func.sum(Segment.character_count), 0),
                func.coalesce(func.sum(Segment.token_count), 0)
            ).filter(Segment.document_id == document.id).first()
            # 10.更新文档的对应信息
            self.update(
                document,
                character_count=document_character_count,
                token_count=document_token_count,
            )
            # 11.更新关键词表信息
            if document.enabled is True:
                self.keyword_table_service.add_keyword_table_from_ids(dataset_id, [segment.id])
        except Exception as e:
            logging.exception(f"新增文档片段内容发生异常，错误信息{str(e)}")
            if segment:
                self.update(
                    segment,
                    error=str(e),
                    enabled=False,
                    status=SegmentStatus.ERROR,
                    disabled_at=datetime.now(),
                    stopped_at=datetime.now(),
                )
            raise FailException("新增文档片段失败，请稍后尝试")

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID) -> Segment:
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        # 1.获取片段信息并校验权限
        segment = self.get(Segment, segment_id)
        if (
                segment is None
                or str(segment.account_id) != account_id
                or segment.dataset_id != dataset_id
                or segment.document_id != document_id
        ):
            raise NotFoundException("该文档片段不存在，或无查看权限，请核实后重试")
        return segment

    def update_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID, req: UpdateSegmentReq) -> Segment:
        """根据传递的信息更新指定的文档片段信息"""
        account_id: str = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"
        segment = self.get(Segment, segment_id)
        if segment is None or str(segment.account_id) != account_id or segment.document_id != document_id:
            raise NotFoundException("该文档片段不存在，或无权限修改，请核实后重试")

        # 判断文档是否处于可修改状态
        if segment.status != SegmentStatus.COMPLETED:
            raise FailException("当前片段不可修改状态，请稍后尝试")

        # 检测是否传递了keywords，如果没有传递的话，调用jieba服务生成关键词
        if req.keywords.data is None or len(req.keywords.data) == 0:
            req.keywords.data = self.jieba_service.extract_keywords(req.content.data, 10)

        # 4.计算新内容hash值，用于判断是否需要更新向量数据库以及文档详情
        new_hash = generate_text_hash(req.content.data)
        required_update = new_hash != segment.hash

        try:
            # 更新segment表
            self.update(
                segment,
                content=req.content.data,
                keywords=req.keywords.data,
                hash=new_hash,
                character_count=len(req.content.data),
                token_count=self.embeddings_service.calculate_token_count(req.content.data),
            )
            # 更新片段归属关键词信息
            self.keyword_table_service.delete_keyword_table_from_ids(dataset_id, [segment.id])
            self.keyword_table_service.add_keyword_table_from_ids(dataset_id, [segment.id])

            # 检测是否需要更新文档信息，并且更新到向量数据库
            if required_update:
                document = segment.document
                document_character_count, document_token_count = self.db.session.query(
                    func.coalesce(func.sum(Segment.character_count), 0),
                    func.coalesce(func.sum(Segment.token_count), 0)
                ).filter(Segment.document_id == document.id).first()
                self.update(document, character_count=document_character_count, token_count=document_token_count)

                # 更新向量数据库中对应的信息
                self.vector_database_service.collection.data.update(
                    uuid=str(segment.node_id),
                    properties={
                        "text": req.content.data,
                    },
                    vector=self.embeddings_service.embeddings.embed_query(req.content.data)
                )
        except Exception as e:
            logging.exception(f"更新文档片段记录失败, segment_id: {segment}, 错误信息: {str(e)}")
            raise FailException("更新文档片段记录失败，请稍后尝试")

        return segment

    def update_segment_enabled(self, dataset_id: UUID, document_id: UUID, segment_id: UUID, enabled: bool):
        """根据传递的信息更新文档片段的启用状态信息"""
        # todo:等待授权认证模块完成进行切换调整
        account_id = "12a2956f-b51c-4d9b-bf65-336c5acfc4f3"

        # 1.获取片段信息并校验权限
        segment = self.get(Segment, segment_id)
        if (
                segment is None
                or str(segment.account_id) != account_id
                or segment.dataset_id != dataset_id
                or segment.document_id != document_id
        ):
            raise NotFoundException("该文档片段不存在，或无权限修改，请核实后重试")

        # 2.判断文档片段是否处于可启用/禁用的环境
        if segment.status != SegmentStatus.COMPLETED:
            raise FailException("当前片段不可修改状态，请稍后尝试")

        # 3.判断更新的片段启用状态和数据库的数据是否一致，如果是则抛出错误
        if enabled == segment.enabled:
            raise FailException(f"片段状态修改错误，当前已是{'启用' if enabled else '禁用'}")

        # 4.获取更新片段启用状态，并加锁校验
        cache_key = LOCK_SEGMENT_UPDATE_ENABLED.format(segment_id=segment_id)
        cache_result = self.redis_client.get(cache_key)
        if cache_result is not None:
            raise FailException("当前文档片段正在修改状态，请稍后重新尝试")

        # 5.上锁并更新对应的数据，涵盖postgres记录，weaviate、关键词表
        with self.redis_client.lock(cache_key, LOCK_EXPIRE_TIME):
            try:
                # 6. 修改postgres数据库里的文档片段状态
                self.update(segment, enabled=enabled, disabled_at=None if enabled else datetime.now())
                # 7.更新关键词表对应的信息，有可能新增，也有可能删除
                document = segment.document
                if enabled is True and document.enabled is True:
                    self.keyword_table_service.add_keyword_table_from_ids(dataset_id, [segment_id])
                else:
                    self.keyword_table_service.delete_keyword_table_from_ids(dataset_id, [segment_id])
                # 8.同步处理weaviate向量数据库里的数据
                self.vector_database_service.collection.data.update(
                    uuid=segment.node_id,
                    properties={
                        "segment_enabled": enabled,
                    }
                )
            except Exception as e:
                logging.exception(f"更改文档片段启用状态出现异常，segment_id: {segment_id}, 错误信息: {str(e)}")
                self.update(
                    segment,
                    error=str(e),
                    status=SegmentStatus.ERROR,
                    enabled=False,
                    disabled_at=datetime.now(),
                    stopped_at=datetime.now(),
                )
                raise FailException("更新文档片段启用状态失败，请稍后重新尝试")

    def delete_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        """根据传递的信息删除指定的文档片段信息，该服务是同步方法"""
        # todo:等待授权认证模块完成进行切换调整
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        # 1.获取片段信息并校验权限
        segment = self.get(Segment, segment_id)
        if (
                segment is None
                or str(segment.account_id) != account_id
                or segment.dataset_id != dataset_id
                or segment.document_id != document_id
        ):
            raise NotFoundException("该文档片段不存在，或无权限修改，请核实后重试")

        # 2.判断文档是否处于可以删除的状态，只有COMPLETED/ERROR才可以删除
        if segment.status not in [SegmentStatus.COMPLETED, SegmentStatus.ERROR]:
            raise FailException("当前文档片段处于不可删除状态，请稍后尝试")

        # 3.删除文档片段并获取该片段的文档信息
        document = segment.document
        self.delete(segment)

        # 4.同步删除关键词表中属于该片段的关键词
        self.keyword_table_service.delete_keyword_table_from_ids(dataset_id, [segment_id])

        # 5. 同步删除向量数据库存储的记录
        try:
            self.vector_database_service.collection.data.delete_by_id(str(segment.node_id))
        except Exception as e:
            logging.exception(f"删除文档片段记录失败, segment_id: {segment_id}, 错误信息: {str(e)}")

        # 6. 更新文档信息，涵盖字符串总数、token总次数
        document_character_count, document_token_count = self.db.session.query(
            func.coalesce(func.sum(Segment.character_count), 0),
            func.coalesce(func.sum(Segment.token_count), 0)
        ).filter(Segment.document_id == document.id).first()

        self.update(
            document,
            character_count=document_character_count,
            token_count=document_token_count,
        )
        return segment

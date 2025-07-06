#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 4.7.25 PM2:20
@Author  : tianshiyang
@File    : indexing_service.py
"""
import logging
import re
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import List
from flask import Flask, current_app
from injector import inject
from dataclasses import dataclass
from langchain_core.documents import Document as LCDocument
from redis import Redis
from uuid import UUID

from sqlalchemy import func

from internal.entity.dataset_entity import DocumentStatus, SegmentStatus
from internal.lib.helper import generate_text_hash
from internal.model.dataset import Document, Segment
from internal.service.ProcessRuleService import ProcessRuleService
from internal.service.base_service import BaseService
from internal.service.embeddings_service import EmbeddingsService
from internal.service.jieba_service import JiebaService
from internal.service.keyword_table_service import KeywordTableService
from internal.service.vector_database_service import VectorDatabaseService
from pkg.sqlalchemy import SQLAlchemy
from internal.core.file_extractor import FileExtractor


@inject
@dataclass
class IndexingService(BaseService):
    """勾引构建服务"""
    db: SQLAlchemy
    redis_client: Redis
    file_extractor: FileExtractor
    process_rule_service: ProcessRuleService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    keyword_table_service: KeywordTableService
    vector_database_service: VectorDatabaseService

    def build_documents(self, document_ids: List[UUID]) -> None:
        """根据传递的文档id列表构建知识库文档，涵盖了加载、分割、索引构建、数据存储等内容"""
        # 1.根据传递的文档id获取所有文档
        documents = self.db.session(Document).filter(Document.id.in_(document_ids)).all()

        # 2.执行循环遍历所有文档完成对每个文档的构建
        for document in documents:
            try:
                # 3.更新当前文档为解析中
                self.update(document, status=DocumentStatus.PARSING, processing_started_at=datetime.now())
                # 4.执行文档加载步骤，并更新文档的状态与时间
                lc_documents = self._parsing(document)
                # 5.执行文档分割步骤，并更新文档状态与时间，涵盖了片段信息
                lc_segments = self._splitting(document, lc_documents)
                # 6.执行文档索引构建，覆盖关键词提取、向量，并更新数据状态
                self._indexing(document, lc_segments)
                # 7.存储操作，覆盖文档状态更新、以及向量数据的存储
                self._completed(document, lc_segments)

            except Exception as e:
                logging.error(f"构建文档发生错误，错误信息：{str(e)}")
                self.update(
                    document,
                    status=DocumentStatus.ERROR,
                    error=str(e),
                    stopped_at=datetime.now()
                )

    def _parsing(self, document: Document) -> List[LCDocument]:
        """解析传递的文档为LangChain文档列表"""
        # 1. 获取upload_file并加载langchain文档
        upload_file = document.upload_file
        lc_documents = self.file_extractor.load(upload_file, False, True)

        # 2.循环处理langChain文档，并删除多余空白字符串
        for lc_document in lc_documents:
            lc_document.page_content = self._clean_extra_text(lc_document.page_content)

        # 3. 更新文档并记录时间
        self.update(
            document,
            character_count=sum([len(lc_document.page_content) for lc_document in lc_documents]),  # 字符总数
            status=DocumentStatus.SPLITTING,
            parsing_completed_at=datetime.now(),
        )
        return lc_documents

    def _splitting(self, document: Document, lc_documents: List[LCDocument]) -> List[LCDocument]:
        """根据传递的信息进行文档分割，拆分成小块片段"""
        # 1. 根据process_rule获取文本分割器
        process_rule = document.process_rule
        text_splitter = self.process_rule_service.get_text_splitter_by_process_rule(
            process_rule,
            self.embeddings_service.calculate_token_count
        )
        # 2.按照process_rule规则清除多余的字符串
        for lc_document in lc_documents:
            lc_document.page_content = self.process_rule_service.clean_text_by_process_rule(
                lc_document.page_content,
                process_rule
            )
        # 3. 分割文档列表为片段列表
        lc_segments = text_splitter.split_documents(lc_documents)
        # 4. 获取对应文档下得到最大片段位置
        position = self.db.session.query(func.coalesce(func.max(Segment.position), 0)).filter(
            Segment.document_id == document.id,
        ).scalar()
        # 5.循环处理片段数据并添加元数据，同时存储到postgres数据库中
        segments = []
        for lc_segment in lc_segments:
            position += 1
            content = lc_segment.page_content
            segment = self.create(
                Segment,
                account_id=document.account_id,
                dataset_id=document.dataset_id,
                document_id=document.id,
                node_id=uuid.uuid4(),
                position=position,
                content=content,
                character_count=len(content),
                token_count=self.embeddings_service.calculate_token_count(content),
                hash=generate_text_hash(content),
                status=SegmentStatus.WAITING,
            )
            lc_segment.metadata = {
                "account_id": str(document.account_id),
                "dataset_id": str(document.dataset_id),
                "document_id": str(document.id),
                "segment_id": str(segment.id),
                "node_id": str(segment.node_id),
                "document_enabled": False,
                "segment_enabled": False,
            }
            segments.append(segment)
        # 6.更新文档的数据，涵盖状态、token数等内容
        self.update(
            document,
            token_count=sum([segment.token_count for segment in segments]),
            status=DocumentStatus.INDEXING,
            splitting_completed_at=datetime.now(),
        )
        return lc_documents

    def _indexing(self, document: Document, lc_segments: List[LCDocument]) -> None:
        """根据传递的信息构建索引，覆盖关键词提取、词表构建"""
        for lc_segment in lc_segments:
            # 1. 提取每一个片段对应的关键词，关键词的数量最多不超过10个
            keywords = self.jieba_service.extract_keywords(lc_segment.page_content, 10)

            # 2. 逐条更新文档片段的关键词
            self.db.session.query(Segment).filter(
                Segment.id == lc_segment.metadata["segment_id"],
            ).update({
                "keywords": keywords,
                "status": SegmentStatus.INDEXING,
                "indexing_completed_at": datetime.now(),
            })
            # 3.获取当前知识库的关键词表
            keyword_table_record = self.keyword_table_service.get_keyword_table_from_dataset_id(document.dataset_id)
            keyword_table = {
                field: set(value) for field, value in keyword_table_record.keyword_table.items()
            }

            # 4. 循环将新关键词添加到关键词表中
            for keyword in keywords:
                if keyword not in keyword_table:
                    keyword_table[keyword] = set()
                keyword_table[keyword].add(lc_segment.metadata["segment_id"])
            # 5.更新关键词表
            self.update(
                keyword_table_record,
                keyword_table={field: list(value) for field, value in keyword_table.items()}
            )
        # 6.更新文档状态
        self.update(document, indexing_completed_at=datetime.now())

    def _completed(self, document: Document, lc_segments: List[LCDocument]) -> None:
        """存储文档片段到向量数据库，并完成状态更新"""
        # 1. 循环遍历片段列表数据，将文档状态及片段状态设置成True
        for lc_segment in lc_segments:
            lc_segment.metadata["document_enabled"] = True
            lc_segment.metadata["segment_enabled"] = True

        # 2. 调用向量数据库，每次存储10条数据，避免一次传递过多的数据
        def thread_func(flask_app: Flask, chunks: list[LCDocument], ids: list[UUID]) -> None:
            with flask_app.app_context():
                try:
                    self.vector_database_service.vector_store.add_documents(
                        chunks,
                        ids=ids,
                    )
                    with self.db.auto_commit():
                        self.db.session.query(Segment).filter(
                            Segment.node_id.in_(ids),
                        ).update({
                            "status": SegmentStatus.COMPLETED,
                            "completed_at": datetime.now(),
                            "enabled": True,
                        })
                except Exception as e:
                    logging.exception(f"构建文档片段索引发生异常，错误信息： {str(e)}")
                    with self.db.auto_commit():
                        self.db.session.query(Segment).filter(
                            Segment.note_id.in_(ids)
                        ).update({
                            "status": SegmentStatus.ERROR,
                            "completed_at": datetime.now(),
                            "stopped_at": datetime.now(),
                            "enabled": False,
                        })

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(0, len(lc_segments), 10):
                chunks = lc_segments[i:i + 10]
                ids = [chunk.metadata["node_id"] for chunk in chunks]
                futures.append(executor.submit(thread_func, current_app._get_current_object(), chunks, ids))

            for future in futures:
                future.result()

    @classmethod
    def _clean_extra_text(cls, text: str) -> str:
        """清除过滤传递的多余空白字符串"""
        text = re.sub(r'<\|', '<', text)
        text = re.sub(r'\|>', '>', text)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\xEF\xBF\xBE]', '', text)
        text = re.sub('\uFFFE', '', text)  # 删除零宽非标记字符
        return text

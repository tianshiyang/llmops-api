#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.8.25 AM11:20
@Author  : tianshiyang
@File    : ai_service.py
"""
import json
import os
from dataclasses import dataclass
from typing import Generator

from injector import inject
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from internal.entity.ai_entity import OPTIMIZE_PROMPT_TEMPLATE
from internal.exception import ForbiddenException
from internal.model import Account, Message
from internal.service.base_service import BaseService
from internal.service.conversation_service import ConversationService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AiService(BaseService):
    """AI服务"""
    conversation_service: ConversationService
    db: SQLAlchemy

    def generate_suggested_questions_from_message_id(self, message_id, account: Account) -> list[str]:
        """根据传递的消息id+账号生成建议问题列表"""
        # 1.查询消息并校验权限信息
        message = self.get(Message, message_id)
        if not message or message.created_by != account.id:
            raise ForbiddenException("该条消息不存在或无权限")

        # 2.构建对话历史列表
        histories = f"Human: {message.query}\nAI: {message.answer}"

        return self.conversation_service.generate_suggested_questions(histories)

    @classmethod
    def optimize_prompt(cls, prompt: str) -> Generator[str, None, None]:
        """根据传递的prompt进行优化生成"""
        # 1.构建优化prompt的模版提示词
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", OPTIMIZE_PROMPT_TEMPLATE),
            ("human", "{prompt}")
        ])

        # 2.构建LLM
        llm = ChatOpenAI(model=os.getenv("BASE_CHAT_MODEL"), temperature=0.5)

        # 3.组装优化链
        optimize_chain = prompt_template | llm | StrOutputParser()

        # 4.调用链并流式事件返回
        for optimize_prompt in optimize_chain.stream({"prompt": prompt}):
            # 5.组装相应数据
            data = {"optimize_prompt": optimize_prompt}
            yield f"event: optimize_prompt\ndata: {json.dumps(data)}\n\n"

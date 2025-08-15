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
from internal.service.base_service import BaseService


@inject
@dataclass
class AiService(BaseService):
    """AI服务"""

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

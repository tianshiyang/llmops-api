#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM4:31
@Author  : tianshiyang
@File    : chat.py
"""
from internal.core.language_model.entities.model_entity import BaseLanguageModel
from langchain_openai import ChatOpenAI


class Chat(ChatOpenAI, BaseLanguageModel):
    """OpenAI聊天模型基类"""
    pass

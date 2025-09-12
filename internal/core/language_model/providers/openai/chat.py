#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM4:31
@Author  : tianshiyang
@File    : chat.py
"""
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI


class Chat(ChatOpenAI, BaseLanguageModel):
    """OpenAI聊天模型基类"""
    pass

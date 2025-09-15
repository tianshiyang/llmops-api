#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM4:29
@Author  : tianshiyang
@File    : chat.py
"""
from langchain_community.chat_models import ChatOllama
from internal.core.language_model.entities.model_entity import BaseLanguageModel


class Chat(ChatOllama, BaseLanguageModel):
    """Ollama聊天模型"""
    pass

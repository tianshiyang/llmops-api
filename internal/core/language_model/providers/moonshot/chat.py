#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 12.9.25 PM2:32
@Author  : tianshiyang
@File    : chat.py.py
"""
from langchain_community.chat_models import MoonshotChat
from langchain_core.language_models import BaseLanguageModel


class Chat(MoonshotChat, BaseLanguageModel):
    """月之暗面聊天模型"""
    pass

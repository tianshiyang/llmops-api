#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/5/11 22:39
@Author  : tianshiyang
@File    : 1.对话消息历史组件基础.py
"""
from langchain_core.chat_history import InMemoryChatMessageHistory

memory = InMemoryChatMessageHistory()

memory.add_user_message("我是慕小课，你是谁")
memory.add_ai_message("你好，我是ChatGPT，有什么可以帮到您的？")

print(memory.messages)

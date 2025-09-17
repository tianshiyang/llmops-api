#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 17.9.25 AM8:35
@Author  : tianshiyang
@File    : conversation_handler.py
"""
from dataclasses import dataclass

from flask_login import login_required
from injector import inject

from internal.service import ConversationService
from uuid import UUID


@inject
@dataclass
class ConversationHandler:
    """会话处理器"""
    conversation_service: ConversationService

    @login_required
    def get_conversation_messages_with_page(self, conversation_id: UUID):
        """根据传递的会话id获取该会话的消息列表分页数据"""
        pass

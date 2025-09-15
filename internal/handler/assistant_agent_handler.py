#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.9.25 PM9:21
@Author  : tianshiyang
@File    : assistant_agent_handler.py
"""
from dataclasses import dataclass

from flask_login import login_required, current_user
from injector import inject

from internal.schema.assistant_agent_schema import AssistantAgentChat
from internal.service import AssistantAgentService
from pkg.response import validate_error_json
from pkg.response.response import compact_generate_response


@inject
@dataclass
class AssistantAgentHandler:
    """辅助智能体处理器"""
    assistant_agent_service: AssistantAgentService

    @login_required
    def assistant_agent_chat(self):
        """与辅助智能体进行对话聊天"""
        # 1.提取请求数据并校验
        req = AssistantAgentChat()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务创建会话相应
        response = self.assistant_agent_service.chat(req.query.data, current_user)
        return compact_generate_response(response)

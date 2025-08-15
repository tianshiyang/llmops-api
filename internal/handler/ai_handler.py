#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 15.8.25 AM11:18
@Author  : tianshiyang
@File    : ai_handler.py
"""
from flask_login import login_required
from injector import inject
from dataclasses import dataclass

from internal.schema.ai_schema import OptimizePromptReq
from internal.service.ai_service import AiService
from pkg.response import validate_error_json
from pkg.response.response import compact_generate_response


@inject
@dataclass
class AiHandler:
    """AI辅助模块处理器"""
    ai_service: AiService

    @login_required
    def optimize_prompt(self):
        """根据传递的预设prompt进行优化"""
        req = OptimizePromptReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务优化prompt
        resp = self.ai_service.optimize_prompt(req.prompt.data)

        return compact_generate_response(resp)

#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.9.25 PM6:26
@Author  : tianshiyang
@File    : analysis_handler.py
"""
from injector import inject
from dataclasses import dataclass
from flask_login import current_user

from internal.service import AnalysisService
from uuid import UUID

from pkg.response import success_json


@inject
@dataclass
class AnalysisHandler:
    """统计分析处理器"""
    analysis_service: AnalysisService

    # todo:缺少login_required装饰
    def get_app_analysis(self, app_id: UUID):
        """根据传递的应用id获取应用的统计信息"""
        app_analysis = self.analysis_service.get_app_analysis(app_id, current_user)
        return success_json(app_analysis)

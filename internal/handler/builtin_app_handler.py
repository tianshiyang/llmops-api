#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 30.8.25 PM11:31
@Author  : tianshiyang
@File    : builtin_app_handler.py
"""
from flask_login import login_required

from internal.schema.builtin_app_schema import GetBuiltinAppCategoriesResp
from internal.service.builtin_app_service import BuiltinAppService
from pkg.response import success_json
from dataclasses import dataclass
from injector import inject


@inject
@dataclass
class BuiltinAppHandler:
    """LLMOps内置应用处理器"""
    builtin_app_service: BuiltinAppService

    @login_required
    def get_builtin_app_categories(self):
        """获取内置应用分类列表信息"""
        categories = self.builtin_app_service.get_categories()
        resp = GetBuiltinAppCategoriesResp(many=True)
        return success_json(resp.dump(categories))

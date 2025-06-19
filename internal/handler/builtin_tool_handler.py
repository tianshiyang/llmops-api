#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.6.25 PM11:52
@Author  : tianshiyang
@File    : builtin_tool_handler.py
"""
import io
from dataclasses import dataclass
from typing import Any

from flask import send_file
from injector import inject

from internal.service import BuiltinToolService
from pkg.response import success_json


@inject
@dataclass
class BuiltinToolHandler:
    # 内置工具处理类
    builtin_tool_service: BuiltinToolService

    def get_categories(self) -> list[dict[str, Any]]:
        """获取所有内置提供商的分类信息"""
        categories = self.builtin_tool_service.get_categories()
        return success_json(categories)

    def get_builtin_tools(self) -> list[dict[str, Any]]:
        tools = self.builtin_tool_service.get_builtin_tools()
        return success_json(tools)

    def get_provider_icon(self, provider_name: str):
        icon, mimetype = self.builtin_tool_service.get_get_provider_icon(provider_name)
        return send_file(io.BytesIO(icon), mimetype=mimetype)

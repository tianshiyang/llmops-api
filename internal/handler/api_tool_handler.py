#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.6.25 PM9:09
@Author  : tianshiyang
@File    : api_tool_handler.py
"""
from dataclasses import dataclass
from injector import inject

from internal.schema.api_tool_schema import CreateApiToolReq
from internal.service.api_tool_service import ApiToolService
from pkg.response import validate_error_json, success_message


@inject
@dataclass
class ApiToolHandler:
    api_tool_service: ApiToolService

    def create_api_tool_provider(self):
        """创建自定义API工具"""
        req = CreateApiToolReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.api_tool_service.create_api_tool(req)
        return success_message("创建自定义API插件成功")

    def validate_openapi_schema(self):
        """校验openapi_schema是否正确"""
        req = CreateApiToolReq()
        if req.validate():
            return validate_error_json(req.errors)
        self.api_tool_service.parse_openapi_schema(req.openapi_schema.data)
        return success_message("校验成功")

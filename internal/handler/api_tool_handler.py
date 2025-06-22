#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 21.6.25 PM9:09
@Author  : tianshiyang
@File    : api_tool_handler.py
"""
import json
from dataclasses import dataclass

from flask import request
from injector import inject

from internal.schema.api_tool_schema import CreateApiToolReq, GetApiToolProvidersWithPageReq, \
    GetApiToolProvidersWithPageResp
from internal.service.api_tool_service import ApiToolService
from pkg.paginator.paginator import PageModel
from pkg.response import validate_error_json, success_message, success_json


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

    def get_api_tool_providers_with_page(self):
        """获取自定义API工具服务提供者分页列表数据"""
        req = GetApiToolProvidersWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        api_tool_providers, paginator = self.api_tool_service.get_api_tool_providers_with_page(req)
        resp = GetApiToolProvidersWithPageResp(many=True)
        return success_json(PageModel(list=resp.dump(api_tool_providers), paginator=paginator))

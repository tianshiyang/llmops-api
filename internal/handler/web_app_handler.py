#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 16.9.25 PM9:51
@Author  : tianshiyang
@File    : web_app_handler.py
"""
from flask_login import login_required, current_user
from injector import inject
from dataclasses import dataclass

from internal.schema.web_app_schema import GetWebAppResp, WebAppChatReq
from internal.service import WebAppService
from pkg.response import success_json, validate_error_json
from pkg.response.response import compact_generate_response


@inject
@dataclass
class WebAppHandler:
    web_app_service: WebAppService

    @login_required
    def get_web_app(self, token: str):
        """根据传递的token凭证标识获取WebApp基础信息"""
        # 1.调用服务根据传递的token获取应用信息
        app = self.web_app_service.get_web_app(token)

        # 2.构建响应结构并返回
        resp = GetWebAppResp()
        return success_json(resp.dump(app))

    @login_required
    def web_app_chat(self, token: str):
        """根据传递的token+query等信息与WebApp进行对话"""
        # 1.提取请求并校验
        req = WebAppChatReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务获取对应响应内容
        response = self.web_app_service.web_app_chat(token, req, current_user)

        return compact_generate_response(response)
